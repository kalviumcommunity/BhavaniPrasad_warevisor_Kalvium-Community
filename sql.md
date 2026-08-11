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

Use PostgreSQL for the application database. The connection helper and authentication logic live in [scripts/db_connect.py](scripts/db_connect.py) and schema definitions live in [sql/postgres_schema.sql](sql/postgres_schema.sql).

```sql
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
```

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