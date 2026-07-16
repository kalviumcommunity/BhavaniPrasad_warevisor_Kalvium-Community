"""SQLite database setup for the warehouse inventory workflow."""

from __future__ import annotations

import sqlite3
from pathlib import Path


DEFAULT_DATABASE_PATH = Path("data/warehouse_inventory.db")


def get_connection(database_path: str | Path = DEFAULT_DATABASE_PATH) -> sqlite3.Connection:
    """Open a SQLite connection and enable foreign key support."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def create_tables(connection: sqlite3.Connection) -> None:
    """Create the core warehouse tables if they do not already exist."""
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('sender', 'manager'))
        );

        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT,
            SKU TEXT NOT NULL UNIQUE,
            sender_id INTEGER NOT NULL,
            FOREIGN KEY (sender_id) REFERENCES Users (id)
        );

        CREATE TABLE IF NOT EXISTS Inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            warehouse TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
            status TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES Products (product_id)
        );

        CREATE TABLE IF NOT EXISTS Shipments (
            shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            shipment_date DATE NOT NULL,
            FOREIGN KEY (sender_id) REFERENCES Users (id),
            FOREIGN KEY (product_id) REFERENCES Products (product_id)
        );

        CREATE TABLE IF NOT EXISTS Returns (
            return_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            reason TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES Products (product_id)
        );
        """
    )
    connection.commit()


def initialize_database(database_path: str | Path = DEFAULT_DATABASE_PATH) -> Path:
    """Create the SQLite database file and initialize the schema."""
    path = Path(database_path)
    with get_connection(path) as connection:
        create_tables(connection)
    return path


if __name__ == "__main__":
    db_path = initialize_database()
    print(f"[OK] Database initialized at {db_path}")