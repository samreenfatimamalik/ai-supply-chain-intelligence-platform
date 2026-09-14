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

- Set up project folder structure (api, data, ml, dashboard, notebooks, tests, docker etc)
- Configured PostgreSQL running inside a Docker container
- Initialized Git repository and pushed to GitHub
- Designed and created database schema — 6 core tables: warehouses, suppliers, skus, inventory, orders, shipments (with relationships and indexes)
- Synthetic dataset generated (50 warehouses, 5k SKUs, 400 suppliers, 150k orders, 137.9k shipments) using Faker + statistical distributions with seasonal and reliability
- Dataset loaded into PostgreSQL via Docker container (bulk COPY load)
- Set up FastAPI application with modular structure (api/main.py, database.py, models, schemas, routers)
- Configured SQLAlchemy connection to PostgreSQL via .env
- Built SQLAlchemy models for warehouses, suppliers, skus, orders tables
- Created Pydantic response schemas for API serialization
- Implemented read CRUD endpoints (GET list + GET by id) for warehouses, SKUs, and orders
- Verified all endpoints working via FastAPI's auto-generated Swagger UI (/docs)
- Created dedicated conda environment "supplychain" for project dependency isolation
## Demand Forecasting
- Forecasts overall daily demand using Prophet (multiplicative seasonality)
- Evaluated on a 90-day holdout: MAE ≈ 130, RMSE ≈ 164, R² ≈ 0.43
- LightGBM (with lag/rolling features) was also tested but did not outperform Prophet on this dataset
- R² is below the 0.70 target; attributed to intentional randomness in the synthetic order data — the model correctly captures trend and Nov/Dec seasonality (see notebook plots) but daily-level noise limits point-prediction accuracy
- Forecasting API endpoint (`POST /forecast/predict`) — takes a horizon (7/14/30/90 days) and returns predicted demand with confidence bounds from the trained Prophet model
