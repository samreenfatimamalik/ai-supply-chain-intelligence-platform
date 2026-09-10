from fastapi import FastAPI
from api.database import engine
from sqlalchemy import text
from api.routers import warehouses, skus, orders

app = FastAPI(title="AI Supply Chain Intelligence Platform")

app.include_router(warehouses.router)
app.include_router(skus.router)
app.include_router(orders.router)


@app.get("/")
def read_root():
    return {"message": "Supply Chain API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/test-db")
def test_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"db_connection": "success", "result": result.fetchone()[0]}