# Docker 部署指南

本文提供 R20 Quantum Trader 的 Docker Compose 部署方式，适用于 Linux 服务器、NAS、云主机和 Docker Desktop。

## 运行结构

R20 当前的 Gateway Worker 已经拥有调度器和通知投递能力。Docker 部署只启动一个 `app` 容器：

- FastAPI 控制面：监听容器内 `8080` 端口
- Gateway Supervisor：由 FastAPI 生命周期启动
- Gateway Worker：负责交易周期、因子刷新、新闻刷新、通知投递和备份调度
- 前端：在镜像构建阶段生成并由 FastAPI 提供

**不要额外启动 `r20_backend.scheduler` 或 `deploy/r20-scheduler.service`。** 那是旧版兼容组件，与 Gateway Worker 并行运行会造成重复调度风险。

## 首次部署

在项目根目录执行：

```bash
cp env.example .env
chmod 600 .env
```

编辑 `.env`，首次建议保持模拟盘：

```dotenv
R20_OKX_ENV=demo
OKX_DEMO_API_KEY=
OKX_DEMO_SECRET_KEY=
OKX_DEMO_PASSPHRASE=
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_llm_api_key
LLM_MODEL=gemini-3.7-flash-high
R20_SETUP_TOKEN=replace_with_a_long_random_setup_token
```

构建并启动：

```bash
docker compose -f compose.yaml build
docker compose -f compose.yaml up -d
```

查看状态和日志：

```bash
docker compose -f compose.yaml ps
docker compose -f compose.yaml logs -f app
```

健康检查：

```bash
curl http://127.0.0.1:8080/health
```

浏览器访问：

- 前台大屏：`http://服务器地址:8080/`
- 管理后台：`http://服务器地址:8080/admin`

第一次进入管理后台时使用 `R20_SETUP_TOKEN` 初始化管理员账号。初始化完成后，建议在后台设置永久管理员凭据，并保管好配置 volume。

## 端口和运行参数

Compose 默认将宿主机 `8080` 映射到容器 `8080`。如需修改宿主机端口，在 `.env` 末尾加入：

```dotenv
R20_HTTP_PORT=18080
```

然后重新创建容器：

```bash
docker compose up -d --force-recreate
```

容器固定使用非 root 用户 `r20`（UID/GID `10001:10001`）运行。Compose 默认使用 named volumes，因此不需要修改宿主机目录权限。恢复外部备份时，应确保 volume 内文件对 UID `10001` 可读写。

## 持久化数据

Compose 使用以下 named volumes：

| Volume | 用途 |
|---|---|
| `r20-quantum-trader_r20_config` | 后台通过 UI 更新后的运行时 `.env` |
| `r20-quantum-trader_r20_data` | SQLite、加密密钥、交易快照、策略配置和持仓状态 |
| `r20-quantum-trader_r20_logs` | Gateway、后台和审计日志 |
| `r20-quantum-trader_r20_backups` | 本地备份目标 |
| `r20-quantum-trader_r20_okx` | 可选的 OKX CLI OAuth 状态 |
| `r20-quantum-trader_r20_bypy` | 可选的 ByPy/Baidu OAuth 状态 |
| `r20-quantum-trader_r20_npm` | 用户级 npm 目录 |

查看 volume：

```bash
docker volume ls | grep r20-quantum-trader
```

**不要使用 `docker compose down -v`，除非你确认要删除全部运行数据和密钥。** 普通升级不会删除 named volumes。

## 升级二开版本

Docker 镜像内不执行 Git pull。后台的“更新应用”接口在 Docker 模式下会明确提示由宿主机管理更新，这是为了避免容器内修改不可持久化，以及运行中的代码和镜像版本不一致。

从当前 Git 分支升级：

```bash
git pull --ff-only origin dev
docker compose -f compose.yaml build --pull
docker compose -f compose.yaml up -d
```

如果使用新的镜像标签，可以在 `.env` 设置 `R20_IMAGE`，并改用远程镜像 Compose 配置。

## Docker Hub 访问受限

如果服务器无法直接访问 Docker Hub，可在 `.env` 指定兼容的镜像代理：

```dotenv
R20_NODE_IMAGE=你的镜像代理/node:22-alpine
R20_PYTHON_IMAGE=你的镜像代理/python:3.12-alpine
```

也可以在 Docker daemon 中统一配置 registry mirror。基础镜像名称通过构建参数注入，不需要修改 Dockerfile。
## OKX 凭据模式

服务器部署优先使用环境专属 API Key：

- `R20_OKX_ENV=demo` 对应 `OKX_DEMO_*`
- `R20_OKX_ENV=live` 对应 `OKX_LIVE_*`
- API Key 不要授予提现权限，并尽可能绑定服务器 IP
- 实盘前先在 DEMO 模式完成策略、风控、通知和备份演练

镜像同时包含 Node.js、npm 和官方 `okx` CLI，方便检查 CLI 依赖。CLI OAuth 属于可选方案，认证状态保存在 `r20_okx` volume 中；不要把该 volume 或导出的 `.okx` 目录复制到其他用户或提交到 Git。

## 备份和恢复

R20 的后台配置、SQLite 数据库和加密密钥位于 `r20_data` volume。建议同时做两层备份：

1. 使用 R20 后台配置的远端备份目标；
2. 使用 Docker 主机定期备份 named volumes。

示例：

```bash
docker run --rm \
  -v r20-quantum-trader_r20_data:/source:ro \
  -v "$PWD:/backup" \
  alpine tar czf /backup/r20-data-$(date +%Y%m%d).tar.gz -C /source .
```

恢复前先停止应用：

```bash
docker compose down
# 将经过验证的备份解压回对应 volume
docker compose up -d
```

## 反向代理和 HTTPS

生产环境建议让 Caddy、Nginx 或 Traefik 终止 HTTPS，再反向代理到宿主机 `127.0.0.1:${R20_HTTP_PORT}`。不要直接把管理后台暴露在公网而不设置管理员账号、强随机 `R20_SETUP_TOKEN` 和访问控制。

## 排查命令

```bash
# 查看容器和健康状态
docker compose ps

# 查看最近 200 行应用日志
docker compose logs --tail=200 app

# 检查健康接口
docker compose exec app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/health').read().decode())"

# 检查 OKX CLI、Node 和 npm
docker compose exec app python scripts/r20_okx_setup.py

# 进入只读 shell（不建议在容器内修改代码）
docker compose exec app sh
```

如果容器反复重启，先执行：

```bash
docker compose logs --tail=300 app
docker inspect --format '{{json .State.Health}}' $(docker compose ps -q app)
```
