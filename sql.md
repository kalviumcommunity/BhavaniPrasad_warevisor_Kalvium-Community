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

Create tables such as:

Users
Field	Type
id	INTEGER
name	TEXT
email	TEXT
password	TEXT
role	sender / manager
Products
Field	Type
product_id	INTEGER
product_name	TEXT
category	TEXT
SKU	TEXT
sender_id	INTEGER
Inventory
Field	Type
inventory_id	INTEGER
product_id	INTEGER
warehouse	TEXT
quantity	INTEGER
status	TEXT
Shipments
Field	Type
shipment_id	INTEGER
sender_id	INTEGER
product_id	INTEGER
quantity	INTEGER
shipment_date	DATE
Returns
Field	Type
return_id	INTEGER
product_id	INTEGER
quantity	INTEGER
reason	TEXT