# WareVisor / RetailStock Manager - Manager Dashboard Guide

This document summarizes the **Manager Dashboard (Summary)** page built according to the wireframe specification for **ROLE 1: MANAGER**.

---

## 🌟 Overview of Implemented Features

### 1. Sidebar Navigation
- Dark Navy (`#0f172a`) branding panel displaying **WareVisor - RetailStock Manager**.
- Highlighted active navigation item: **1. Manager Dashboard (Summary)**.
- Full menu options: *Dashboard, All Products, Add Product, Stock Movements, Reports, Alerts, Users, Settings, Logout*.

### 2. Top Header & Action Controls
- Role banner: `ROLE 1: MANAGER`.
- Live real-time search box: Filters warehouses & recent stock movements as you type.
- **Export Report** button: Downloads a CSV overview of key dashboard metrics.
- User profile widget displaying **Manager (Central Admin)**.

### 3. Top 4 KPI Metrics Cards
- **Total Products**: `1,248` (All Warehouses, +4.2% MoM)
- **Total Stock**: `45,780` (All Warehouses, +12.5% MoM)
- **Low Stock Products**: `86` (Reorder Soon warning badge, click to trigger details modal)
- **Out of Stock**: `12` (Critical danger badge, click to trigger reorder modal)

### 4. Interactive Analytics Charts
- **Stock Overview Chart** (Line & Gradient Area Chart):
  - Tracks stock accumulation over months (Jan - Aug) with smooth spline interpolation.
  - Interactive filter dropdown (*This Year, This Quarter, This Month*).
- **Stock by Category Chart** (Donut Chart & Legend):
  - Visualizes inventory distribution: **Electronics (41%)**, **Clothing (25%)**, **Home & Kitchen (18%)**, **Beauty (10%)**, **Others (6%)**.

### 5. Warehouse Ranks & Activity Feed
- **Top Warehouses by Stock**:
  1. Central Warehouse (New Delhi - 18,500 units - 85% capacity)
  2. North Zone Warehouse (Delhi - 12,300 units - 65% capacity)
  3. South Zone Warehouse (Bangalore - 8,850 units - 45% capacity)
- **Recent Stock Movements**:
  - Inbound & outbound transaction feed with status indicators (+150 units Wireless Mouse, -45 units Workstation Chair, +300 units T-Shirt).

### 6. Modals & Interactive Drawers
- **Low & Out of Stock Modal**: Click on Low Stock or Out of Stock cards to open a detailed table of critical SKUs.
- **All Warehouses Modal**: Click "View All" on Warehouses card to view all location details.

---

## 🚀 How to View the Dashboard

### Method 1: Web Application (Browser - Recommended)
Simply double-click [`index.html`](file:///c:/Users/mindy/3wi/BhavaniPrasad_warevisor_Kalvium-Community/index.html) or run the launcher script:

```bash
python run_dashboard.py
```
This launches a local web server at `http://localhost:8080` and opens it in your default browser.

### Method 2: Streamlit Dashboard
To run via Streamlit:

```bash
streamlit run app.py
```
or
```bash
streamlit run streamlit_app.py
```
