# AI Supply Chain Intelligence Platform

End-to-end AI system for supply chain intelligence — demand forecasting, inventory optimization, supplier risk scoring, alerting, and executive dashboard for a large-scale retail network (120+ warehouses, 45,000+ SKUs, 8,000+ suppliers).

## Tech Stack
Python, FastAPI, PostgreSQL, LightGBM, Prophet, Streamlit, Docker, GitHub Actions

## Modules
1. Data ingestion layer
2. Demand forecasting engine (multi-horizon: 7/14/30/90 days)
3. Inventory optimization system
4. Supplier risk & late shipment prediction
5. Automated alerting layer
6. Executive dashboard
7. SHAP-based explainability

## Progress Log

- Set up project folder structure (api, data, ml, dashboard, notebooks, tests, docker)
- Configured PostgreSQL running inside a Docker container
- Initialized Git repository and pushed to GitHub
- Designed and created database schema — 6 core tables: warehouses, suppliers, skus, inventory, orders, shipments (with relationships and indexes)
- Synthetic dataset generated (50 warehouses, 5k SKUs, 400 suppliers, 150k orders, 137.9k shipments) using Faker + statistical distributions with seasonal and reliability-linked patterns
- Data validated (referential integrity, null checks, value ranges) — all checks passed
- Dataset loaded into PostgreSQL via Docker container (bulk COPY load)
