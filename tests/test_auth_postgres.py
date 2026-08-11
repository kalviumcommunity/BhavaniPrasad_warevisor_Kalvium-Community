"""Tests for PostgreSQL user registration and authentication based on app_users schema."""

import os
import pytest
from sqlalchemy import create_engine, text

from scripts.db_connect import (
    get_engine,
    init_postgres_db,
    register_user,
    authenticate_user,
    get_user_by_email,
    get_user_by_username
)


@pytest.fixture
def db_engine():
    """Returns the PostgreSQL SQLAlchemy engine."""
    engine = get_engine()
    init_postgres_db(engine)
    return engine


def test_init_postgres_db(db_engine):
    """Test that app_users table exists and default seed users are present."""
    with db_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM app_users;")).scalar()
        assert result >= 2, "Default seed users should exist in app_users table."


def test_register_user_success(db_engine):
    """Test registering a new user successfully into app_users PostgreSQL table."""
    test_email = "test_user_unique_1234@warevisor.com"
    test_username = "testuser1234"

    # Cleanup if pre-existing
    with db_engine.begin() as conn:
        conn.execute(text("DELETE FROM app_users WHERE email = :e OR username = :u;"), {"e": test_email, "u": test_username})

    success, result = register_user(
        full_name="Test User",
        email=test_email,
        password_hash="securepass123",
        role="Manager",
        username=test_username,
        engine=db_engine
    )

    assert success is True, f"Registration failed: {result}"
    assert isinstance(result, dict)
    assert result["username"] == test_username
    assert result["email"] == test_email
    assert result["role"] == "manager"
    assert result["status"] == "active"

    # Cleanup after test
    with db_engine.begin() as conn:
        conn.execute(text("DELETE FROM app_users WHERE email = :e;"), {"e": test_email})


def test_register_duplicate_email_fails(db_engine):
    """Test that registering a duplicate email returns an error."""
    test_email = "dup_email_test@warevisor.com"
    test_username1 = "dupuser1"
    test_username2 = "dupuser2"

    with db_engine.begin() as conn:
        conn.execute(text("DELETE FROM app_users WHERE email = :e;"), {"e": test_email})

    s1, r1 = register_user("User One", test_email, "pass1", "Manager", test_username1, engine=db_engine)
    assert s1 is True

    s2, r2 = register_user("User Two", test_email, "pass2", "Product Sender", test_username2, engine=db_engine)
    assert s2 is False
    assert "already exists" in r2.lower()

    # Cleanup
    with db_engine.begin() as conn:
        conn.execute(text("DELETE FROM app_users WHERE email = :e;"), {"e": test_email})


def test_authenticate_user_by_username_and_email(db_engine):
    """Test login via username and email against app_users table."""
    test_email = "auth_test_user@warevisor.com"
    test_username = "authuser99"

    with db_engine.begin() as conn:
        conn.execute(text("DELETE FROM app_users WHERE email = :e;"), {"e": test_email})

    register_user("Auth User", test_email, "mysecretpass", "Product Sender", test_username, engine=db_engine)

    # Auth by username
    user_by_uname = authenticate_user(test_username, "mysecretpass", engine=db_engine)
    assert user_by_uname is not None
    assert user_by_uname["email"] == test_email
    assert user_by_uname["role"] == "product_sender"

    # Auth by email
    user_by_mail = authenticate_user(test_email, "mysecretpass", engine=db_engine)
    assert user_by_mail is not None
    assert user_by_mail["username"] == test_username

    # Auth failure with wrong password
    bad_auth = authenticate_user(test_username, "wrongpass", engine=db_engine)
    assert bad_auth is None

    # Cleanup
    with db_engine.begin() as conn:
        conn.execute(text("DELETE FROM app_users WHERE email = :e;"), {"e": test_email})
