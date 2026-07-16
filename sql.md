Product Sender
      │
      ▼
Add Product
      │
      ▼
Submit Product Details
      │
      ▼
Database
      │
      ▼
Manager Dashboard
      │
      ▼
Inventory Analysis
      │
      ▼
Reports & Alerts

3. Design the database

Use SQLite for the first version of the app. The connection helper and table creation logic live in [scripts/database_setup.py](scripts/database_setup.py).

```sql
PRAGMA foreign_keys = ON;

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
```