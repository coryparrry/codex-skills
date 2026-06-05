#!/usr/bin/env python3
"""Summarize recent codex-budget-router threads from Codex local state."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path
from typing import Iterable


DEFAULT_DB = Path.home() / ".codex" / "state_5.sqlite"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit recent codex-budget-router model-tier displacement."
    )
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to state_5.sqlite")
    parser.add_argument("--limit", type=int, default=12, help="Number of root threads")
    parser.add_argument("--cwd-like", default=None, help="Optional cwd LIKE filter")
    return parser.parse_args()


def build_where_clause(cwd_like: str | None) -> tuple[str, list[object]]:
    where = """
      agent_role is null
      and (
        first_user_message like '%codex-budget-router%'
        or first_user_message like '%Codex Budget Router%'
        or title like '%codex-budget-router%'
        or title like '%Budget Router%'
      )
    """
    params: list[object] = []
    if cwd_like:
        where += " and cwd like ?"
        params.append(cwd_like)
    return where, params


def audit_sql(where_clause: str) -> str:
    return f"""
    with roots as (
      select id, title, cwd, tokens_used, model, updated_at_ms
      from threads
      where {where_clause}
      order by updated_at_ms desc
      limit ?
    ),
    child as (
      select
        e.parent_thread_id,
        count(*) child_count,
        sum(t.tokens_used) child_tokens,
        sum(
          case when t.agent_role = 'spark_worker' or t.model like '%spark%'
          then 1 else 0 end
        ) spark_count,
        sum(
          case when t.agent_role = 'spark_worker' or t.model like '%spark%'
          then t.tokens_used else 0 end
        ) spark_tokens,
        group_concat(
          coalesce(t.agent_role, 'unknown') || ':' ||
          coalesce(t.model, 'unknown') || ':' ||
          t.tokens_used,
          '; '
        ) child_mix
      from thread_spawn_edges e
      join threads t on t.id = e.child_thread_id
      group by e.parent_thread_id
    )
    select
      roots.id,
      datetime(roots.updated_at_ms / 1000, 'unixepoch', 'localtime') updated,
      roots.cwd,
      roots.model root_model,
      roots.tokens_used root_tokens,
      coalesce(child.child_count, 0) child_count,
      coalesce(child.child_tokens, 0) child_tokens,
      coalesce(child.spark_count, 0) spark_count,
      coalesce(child.spark_tokens, 0) spark_tokens,
      coalesce(child.child_mix, '') child_mix,
      replace(substr(roots.title, 1, 100), char(10), ' ') title
    from roots
    left join child on child.parent_thread_id = roots.id
    order by roots.updated_at_ms desc;
    """


def fetch_rows(db: Path, limit: int, cwd_like: str | None) -> list[sqlite3.Row]:
    where_clause, params = build_where_clause(cwd_like)
    params.append(limit)

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(audit_sql(where_clause), params).fetchall()
    finally:
        conn.close()


def safe_int(row: sqlite3.Row, key: str) -> int:
    return int(row[key] or 0)


def child_share(root_tokens: int, child_tokens: int) -> float:
    total = root_tokens + child_tokens
    return (100.0 * child_tokens / total) if total else 0.0


def has_implementation_worker(child_mix: str) -> bool:
    return "codex_worker:" in child_mix or "spark_worker:" in child_mix


def verdict_for(row: sqlite3.Row) -> str:
    if safe_int(row, "child_count") == 0:
        return "FAIL no workers"
    if safe_int(row, "spark_count") == 0 and has_implementation_worker(row["child_mix"] or ""):
        return "WEAK no Spark"

    share = child_share(safe_int(row, "root_tokens"), safe_int(row, "child_tokens"))
    if share < 20:
        return "WEAK low displacement"
    if share < 30:
        return "OK some displacement"
    return "GOOD material displacement"


def totals(rows: Iterable[sqlite3.Row]) -> dict[str, int]:
    rows = list(rows)
    return {
        "root": sum(safe_int(row, "root_tokens") for row in rows),
        "child": sum(safe_int(row, "child_tokens") for row in rows),
        "workers": sum(safe_int(row, "child_count") for row in rows),
        "spark_workers": sum(safe_int(row, "spark_count") for row in rows),
        "spark_tokens": sum(safe_int(row, "spark_tokens") for row in rows),
        "threads": len(rows),
    }


def print_summary(rows: list[sqlite3.Row]) -> None:
    summary = totals(rows)
    share = child_share(summary["root"], summary["child"])

    print("Budget Router Audit")
    print(f"- Threads: {summary['threads']}")
    print(f"- Root gpt-5.5 tokens: {summary['root']}")
    print(f"- Child worker tokens: {summary['child']}")
    print(f"- Worker threads: {summary['workers']}")
    print(f"- Spark worker threads: {summary['spark_workers']}")
    print(f"- Spark worker tokens: {summary['spark_tokens']}")
    print(f"- Child share: {share:.1f}%")
    print("- Target child share: 30%+ for broad routed work")
    print("- Spark target: use spark_worker for low-risk write/test/docs/script lanes")
    print()


def print_row(row: sqlite3.Row) -> None:
    root = safe_int(row, "root_tokens")
    child = safe_int(row, "child_tokens")
    share = child_share(root, child)

    print(f"{row['updated']} | {verdict_for(row)}")
    print(f"  cwd: {row['cwd']}")
    print(
        f"  root: {row['root_model']} {root} | "
        f"children: {safe_int(row, 'child_count')} {child} ({share:.1f}%) | "
        f"spark: {safe_int(row, 'spark_count')} {safe_int(row, 'spark_tokens')}"
    )
    print(f"  mix: {row['child_mix'] or 'none'}")
    print(f"  title: {row['title']}")
    print()


def main() -> int:
    args = parse_args()
    db = Path(args.db).expanduser()
    if not db.exists():
        raise SystemExit(f"Missing Codex state DB: {db}")

    rows = fetch_rows(db, args.limit, args.cwd_like)
    print_summary(rows)
    for row in rows:
        print_row(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
