# DataBase/db_utils.py
from typing import Sequence, Any, Optional, Dict, List
import sqlite3

def _connect(db_path: str) -> sqlite3.Connection:
    """sqlite 연결 + Row를 dict처럼 쓰도록 설정"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # ✅ 핵심: dict(row) 가능해짐
    return conn

def fetch_one(db_path: str, sql: str, params: Sequence[Any] = ()) -> Optional[Dict[str, Any]]:
    """SELECT 한 건 → dict | None"""
    with _connect(db_path) as conn:
        cur = conn.execute(sql, params or [])
        row = cur.fetchone()
        return dict(row) if row else None   # 이제 안전!

def fetch_all(db_path: str, sql: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
    """SELECT 여러 건 → list[dict]"""
    with _connect(db_path) as conn:
        cur = conn.execute(sql, params or [])
        rows = cur.fetchall()
        return [dict(r) for r in rows]

def execute_query(db_path: str, sql: str, params: Sequence[Any] = ()) -> int:
    """INSERT/UPDATE/DELETE → 영향을 받은 row 수 반환"""
    with _connect(db_path) as conn:
        cur = conn.execute(sql, params or [])
        conn.commit()
        return cur.rowcount
