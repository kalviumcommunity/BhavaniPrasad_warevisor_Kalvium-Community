"""Database connection module for Supabase PostgreSQL with authentication & query helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Load environment variables
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)

# Supabase Postgres default configuration
DEFAULT_HOST = os.getenv("POSTGRES_HOST", "db.pbnlrmcohihvmxxaqgmj.supabase.co")
DEFAULT_PORT = os.getenv("POSTGRES_PORT", "5432")
DEFAULT_USER = os.getenv("POSTGRES_USER", "postgres")
DEFAULT_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
DEFAULT_DB = os.getenv("POSTGRES_DB", "postgres")


def get_db_url(password: Optional[str] = None) -> str:
    """Build PostgreSQL connection URL."""
    pwd = password or DEFAULT_PASSWORD or os.getenv("POSTGRES_PASSWORD", "")
    if not pwd:
        # Fallback to DATABASE_URL if defined
        env_url = os.getenv("DATABASE_URL")
        if env_url and "[YOUR-PASSWORD]" not in env_url and "password" not in env_url:
            return env_url
    
    user = os.getenv("POSTGRES_USER", DEFAULT_USER)
    host = os.getenv("POSTGRES_HOST", DEFAULT_HOST)
    port = os.getenv("POSTGRES_PORT", DEFAULT_PORT)
    db = os.getenv("POSTGRES_DB", DEFAULT_DB)

    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"


def get_engine(password: Optional[str] = None) -> Engine:
    """Get SQLAlchemy Engine for Supabase PostgreSQL."""
    db_url = get_db_url(password)
    return create_engine(db_url, pool_pre_ping=True)


def test_connection(password: Optional[str] = None) -> bool:
    """Test connection to PostgreSQL database."""
    try:
        engine = get_engine(password)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;"))
            return bool(result.scalar() == 1)
    except Exception as err:
        print(f"[DB ERROR] Connection failed: {err}")
        return False


def authenticate_user(username: str, password_hash: str) -> Optional[Dict[str, Any]]:
    """Authenticate user against app_users table and return role info."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            query = text("""
                SELECT user_id, username, full_name, email, role, status
                FROM app_users
                WHERE username = :u AND password_hash = :p AND status = 'active'
            """)
            result = conn.execute(query, {"u": username, "p": password_hash}).mappings().first()
            if result:
                return dict(result)
            return None
    except Exception as err:
        print(f"[AUTH ERROR] Failed to authenticate user '{username}': {err}")
        return None

if __name__ == "__main__":
    print("\nTesting database connection...")
    print(test_connection())
