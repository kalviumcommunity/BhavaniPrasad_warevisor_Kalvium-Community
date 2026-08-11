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


def init_postgres_db(engine: Optional[Engine] = None) -> bool:
    """Initialize PostgreSQL app_users table if not already created."""
    try:
        eng = engine or get_engine()
        with eng.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS app_users (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    role VARCHAR(20) NOT NULL CHECK (role IN ('manager', 'product_sender')),
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))
            # Seed default demo users if empty
            user_count = conn.execute(text("SELECT COUNT(*) FROM app_users;")).scalar()
            if user_count == 0:
                conn.execute(text("""
                    INSERT INTO app_users (username, password_hash, full_name, email, role)
                    VALUES 
                        ('manager', 'manager123', 'Central Warehouse Manager', 'manager@warevisor.com', 'manager'),
                        ('sender', 'sender123', 'Product Dispatch Sender', 'sender@warevisor.com', 'product_sender')
                    ON CONFLICT (username) DO NOTHING;
                """))
        return True
    except Exception as err:
        print(f"[DB ERROR] Failed to initialize PostgreSQL app_users table: {err}")
        return False


def register_user(
    full_name: str,
    email: str,
    password_hash: str,
    role: str,
    username: Optional[str] = None,
    engine: Optional[Engine] = None
) -> tuple[bool, str | Dict[str, Any]]:
    """Register a new user in PostgreSQL app_users table."""
    full_name = full_name.strip()
    email = email.strip().lower()
    
    if not full_name:
        return False, "Full name cannot be empty."
    if not email or "@" not in email or "." not in email:
        return False, "Please enter a valid email address."
    if not password_hash:
        return False, "Password cannot be empty."

    # Normalize role to PostgreSQL check constraint values
    normalized_role = role.strip().lower().replace(" ", "_")
    if normalized_role in ("sender", "product_sender", "productsender"):
        normalized_role = "product_sender"
    elif normalized_role in ("manager", "admin"):
        normalized_role = "manager"
    else:
        return False, "Invalid role specified. Role must be Manager or Product Sender."

    # Derive username if omitted
    uname = username.strip().lower() if username and username.strip() else email.split("@")[0]

    try:
        eng = engine or get_engine()
        init_postgres_db(eng)

        with eng.begin() as conn:
            # Check existing email or username
            existing_email = conn.execute(
                text("SELECT user_id FROM app_users WHERE email = :e"), {"e": email}
            ).first()
            if existing_email:
                return False, f"An account with email '{email}' already exists."

            existing_username = conn.execute(
                text("SELECT user_id FROM app_users WHERE username = :u"), {"u": uname}
            ).first()
            if existing_username:
                return False, f"Username '{uname}' is already taken. Please choose another username."

            # Insert new user
            query = text("""
                INSERT INTO app_users (username, password_hash, full_name, email, role, status)
                VALUES (:username, :password_hash, :full_name, :email, :role, 'active')
                RETURNING user_id, username, full_name, email, role, status, created_at;
            """)
            result = conn.execute(query, {
                "username": uname,
                "password_hash": password_hash,
                "full_name": full_name,
                "email": email,
                "role": normalized_role
            }).mappings().first()

            if result:
                user_dict = dict(result)
                user_dict["created_at"] = str(user_dict["created_at"])
                return True, user_dict
            return False, "Failed to register user record."

    except Exception as err:
        print(f"[AUTH ERROR] Failed to register user '{uname}': {err}")
        return False, f"Database error during registration: {err}"


def authenticate_user(identifier: str, password_hash: str, engine: Optional[Engine] = None) -> Optional[Dict[str, Any]]:
    """Authenticate user against app_users table by username or email and return user dictionary."""
    if not identifier or not password_hash:
        return None

    ident = identifier.strip().lower()

    try:
        eng = engine or get_engine()
        init_postgres_db(eng)
        with eng.connect() as conn:
            query = text("""
                SELECT user_id, username, full_name, email, role, status
                FROM app_users
                WHERE (LOWER(username) = :i OR LOWER(email) = :i)
                  AND password_hash = :p
                  AND status = 'active'
            """)
            result = conn.execute(query, {"i": ident, "p": password_hash}).mappings().first()
            if result:
                return dict(result)
            return None
    except Exception as err:
        print(f"[AUTH ERROR] Failed to authenticate identifier '{identifier}': {err}")
        return None


def get_user_by_email(email: str, engine: Optional[Engine] = None) -> Optional[Dict[str, Any]]:
    """Fetch user record by email address from PostgreSQL."""
    try:
        eng = engine or get_engine()
        with eng.connect() as conn:
            query = text("SELECT user_id, username, full_name, email, role, status FROM app_users WHERE LOWER(email) = :e")
            result = conn.execute(query, {"e": email.strip().lower()}).mappings().first()
            return dict(result) if result else None
    except Exception as err:
        print(f"[DB ERROR] Error fetching user by email: {err}")
        return None


def get_user_by_username(username: str, engine: Optional[Engine] = None) -> Optional[Dict[str, Any]]:
    """Fetch user record by username from PostgreSQL."""
    try:
        eng = engine or get_engine()
        with eng.connect() as conn:
            query = text("SELECT user_id, username, full_name, email, role, status FROM app_users WHERE LOWER(username) = :u")
            result = conn.execute(query, {"u": username.strip().lower()}).mappings().first()
            return dict(result) if result else None
    except Exception as err:
        print(f"[DB ERROR] Error fetching user by username: {err}")
        return None


if __name__ == "__main__":
    print("\nTesting database connection...")
    print(f"Connection test: {test_connection()}")
    print("Initializing PostgreSQL app_users table...")
    print(f"Table init: {init_postgres_db()}")

