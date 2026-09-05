"""Allowlisted, read-only OKX resources for dashboards and diagnostics."""
from __future__ import annotations
from typing import Any
from scripts.okx_runtime import OKXEnvironment
from .okx_trade_service import _request

RESOURCES = {
    "balance": ("/api/v5/account/balance", {}),
    "positions": ("/api/v5/account/positions", {"instType": "SWAP"}),
    "orders": ("/api/v5/trade/orders-pending", {"instType": "SWAP"}),
    "bills": ("/api/v5/account/bills", {"limit": "100"}),
}


def read_private_resource(resource: str, environment: OKXEnvironment, inst_id: str = "") -> list[dict[str, Any]]:
    """Keep one immutable credential/environment snapshot across a cache cycle.

    No trading methods or arbitrary URLs are accepted, and no LIVE fallback is
    attempted when a DEMO request fails. OAuth-only callers retain their CLI path.
    """
    if not environment.configured:
        raise ValueError("当前环境的 API Key 未配置")
    if resource == "algos":
        if not inst_id.endswith("-SWAP"):
            raise ValueError("只读保护单查询需要 SWAP 标的")
        rows = []
        for order_type in ("oco", "conditional"):
            rows.extend(_request("GET", "/api/v5/trade/orders-algo-pending", {
                "instType": "SWAP", "instId": inst_id, "ordType": order_type,
            }, environment, timeout=10))
        return rows
    if resource not in RESOURCES:
        raise ValueError("不支持的账户只读资源")
    path, params = RESOURCES[resource]
    return _request("GET", path, dict(params), environment, timeout=10)
