#!/usr/bin/env python3
"""Start a local, disposable UI preview without live credentials or scheduling.

Build frontend/dist first. Set R20_UI_TEST_PASSWORD for the temporary admin user.
This is a preview, not a deployment command. Python must run in Linux/WSL.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_tests import copy_sources, test_environment


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8081)
    args = parser.parse_args()
    if sys.platform == 'win32':
        parser.error('Run the backend preview in WSL/Linux; do not replace fcntl with a stub.')
    if not 1024 <= args.port <= 65535:
        parser.error('Choose an unprivileged local port between 1024 and 65535.')
    password = os.environ.get('R20_UI_TEST_PASSWORD', '')
    if not 12 <= len(password) <= 128 or not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        parser.error('Set R20_UI_TEST_PASSWORD to a temporary password of 12–128 characters containing letters and digits.')
    if not (ROOT / 'frontend' / 'dist' / 'index.html').is_file():
        parser.error('Build the frontend first: cd frontend && npm run build')
    with tempfile.TemporaryDirectory(prefix='r20-ui-preview-') as temporary:
        root = Path(temporary).resolve()
        copy_sources(root)
        (root / 'frontend' / 'dist').symlink_to(ROOT / 'frontend' / 'dist', target_is_directory=True)
        (root / 'docs').mkdir()
        (root / 'docs' / 'images').symlink_to(ROOT / 'docs' / 'images', target_is_directory=True)
        env = test_environment(root)
        env.update({
            'R20_SETUP_TOKEN': password,
            'R20_DEPLOYMENT_MODE': 'docker',
            'R20_BUILD_BRANCH': 'isolated-ui-preview',
            'R20_BUILD_COMMIT': 'preview-not-production',
            'R20_UI_PREVIEW_PORT': str(args.port),
        })
        # Source snapshots intentionally have no .git. Only the preview process
        # substitutes repository display metadata; the actual application is unchanged.
        bootstrap = (
            'import os, uvicorn; '
            'import r20_backend.app as backend; '
            'backend.git = lambda command: "isolated-ui-preview"; '
            'uvicorn.run(backend.app, host="127.0.0.1", port=int(os.environ["R20_UI_PREVIEW_PORT"]))'
        )
        print(f'Isolated UI preview: http://127.0.0.1:{args.port} (user: admin)', flush=True)
        print('Temporary data only. Background scheduling disabled. Do not enter real credentials.', flush=True)
        try:
            return subprocess.run([sys.executable, '-c', bootstrap], cwd=root, env=env).returncode
        except KeyboardInterrupt:
            return 130


if __name__ == '__main__':
    raise SystemExit(main())
