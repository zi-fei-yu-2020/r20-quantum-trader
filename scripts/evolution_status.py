"""Read-only projection: a completed review is not an approved memory update."""
from pathlib import Path
from contextlib import closing
import json
import sqlite3


def public_status(data_dir=None):
    root = Path(data_dir) if data_dir is not None else Path(__file__).resolve().parents[1] / 'data'
    def read(name, default):
        try:
            value = json.loads((root / name).read_text(encoding='utf8'))
            return value if isinstance(value, type(default)) else default
        except (OSError, ValueError):
            return default
    def text(name):
        try: return (root / name).read_text(encoding='utf8')[:40000]
        except OSError: return ''
    report = read('self_improvement_report.json', {})
    attempt = read('self_improvement_status.json', {})
    memory = read('ai_trading_memory.json', {})
    candidates = read('memory_candidates.json', {}).get('candidates', [])
    if not isinstance(candidates, list): candidates = []
    candidates = [c for c in candidates if isinstance(c, dict)]
    last_job = {}
    db_path = root / 'r20_gateway.db'
    if db_path.exists():
        try:
            with closing(sqlite3.connect(db_path.resolve().as_uri() + '?mode=ro', uri=True, timeout=.2)) as db:
                db.row_factory = sqlite3.Row
                row = db.execute("SELECT status,started_at,finished_at,return_code FROM job_runs WHERE job_name='self_improvement' ORDER BY id DESC LIMIT 1").fetchone()
                if row: last_job = dict(row)
        except sqlite3.Error: pass
    state = attempt.get('status') or ('success' if report.get('timestamp') else 'not_run')
    # The job registry can expose a crash before the engine wrote its own status.
    newer_job = last_job.get('started_at', '').replace('T', ' ')[:19] >= str(attempt.get('last_attempt_at') or report.get('timestamp') or '')[:19]
    if newer_job and last_job.get('status') in ('failed', 'timeout', 'running'):
        state = last_job['status']
    return {
        'status': state,
        'last_attempt_at': attempt.get('last_attempt_at') or last_job.get('started_at'),
        'last_success_at': report.get('completed_at') or report.get('timestamp'),
        'active_memory_updated_at': memory.get('updated_at'),
        'last_job': last_job,
        'review_change_status': report.get('proposed_change_status') or report.get('change_status'),
        'memory_preserved': report.get('memory_preserved', True),
        'sample_size': report.get('total_trades'),
        'win_rate': report.get('win_rate'),
        'insights': report.get('insights') or [],
        # Legacy actions_taken are recommendations, not proof of executed changes.
        'recommendations': report.get('recommendations') or report.get('actions_taken') or [],
        'pending_candidates': sum(c.get('audit_passed') is True and c.get('status') != 'approved' for c in candidates),
        'rejected_candidates': sum(c.get('audit_passed') is False for c in candidates),
        'review_markdown': text('self_improvement_review.md'),
        'message': '复盘结果与运行记忆分开保存；NO_CHANGE 或候选未审核通过时，运行记忆日期不推进。',
    }
