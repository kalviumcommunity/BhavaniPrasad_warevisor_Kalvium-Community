"""Unit tests for SQL Joins & Multi-Table Analysis module."""

from __future__ import annotations

import sys
from pathlib import Path
import pytest
import pandas as pd

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.setup_joins_db import setup_joins_db
from sql.sql_joins_demo import (
    get_connection,
    task_1_left_join_validation,
    task_2_detect_unmatched_keys,
    task_3_compare_join_types,
    task_4_multi_table_join,
    task_5_document_join_decisions,
)


@pytest.fixture(scope="module")
def db_conn(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("data")
    db_path = str(db_dir / "test_joins.db")
    setup_joins_db(db_path)
    conn = get_connection(db_path)
    yield conn
    conn.close()


def test_task_1_left_join_validation(db_conn):
    joined = task_1_left_join_validation(db_conn)
    assert isinstance(joined, pd.DataFrame)
    assert len(joined) == 1000  # 1,000 grouped customers
    assert "order_count" in joined.columns
    assert "total_spent" in joined.columns


def test_task_2_detect_unmatched_keys(db_conn):
    no_orders, orphaned = task_2_detect_unmatched_keys(db_conn)
    assert isinstance(no_orders, pd.DataFrame)
    assert isinstance(orphaned, pd.DataFrame)
    assert len(no_orders) > 0  # Inactive customers present
    assert len(orphaned) == 100  # Exactly 100 orphaned orders created in mock DB


def test_task_3_compare_join_types(db_conn):
    counts = task_3_compare_join_types(db_conn)
    assert "INNER" in counts
    assert "LEFT" in counts
    assert "FULL" in counts
    assert counts["LEFT"] >= counts["INNER"]
    assert counts["FULL"] >= max(counts["LEFT"], 1000)


def test_task_4_multi_table_join(db_conn):
    result = task_4_multi_table_join(db_conn)
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    assert "line_total" in result.columns
    assert "product_name" in result.columns


def test_task_5_document_join_decisions():
    doc = task_5_document_join_decisions()
    assert isinstance(doc, str)
    assert "JOIN STRATEGY DOCUMENTATION" in doc
    assert "Decision 1" in doc
    assert "Decision 2" in doc
    assert "Decision 3" in doc
