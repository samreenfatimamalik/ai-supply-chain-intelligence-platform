import joblib   
from pathlib import Path
from fastapi import APIRouter, HTTPException

from api.schemas import ForecastRequest, ForecastResponse, ForecastPoint

router = APIRouter(prefix="/forecast", tags=["Forecast"])

# Project root is 2 levels up from this file (api/routers/ -> api/ -> root)
MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "models" / "prophet_demand_model.pkl"

# Load the model once when the app starts, not on every request
with open(MODEL_PATH, "rb") as f:
    prophet_model = joblib.load(f)  

ALLOWED_HORIZONS = {7, 14, 30, 90}


@router.post("/predict", response_model=ForecastResponse)
def predict_demand(request: ForecastRequest):
    if request.horizon_days not in ALLOWED_HORIZONS:
        raise HTTPException(
            status_code=400,
            detail=f"horizon_days must be one of {sorted(ALLOWED_HORIZONS)}"
        )

    future = prophet_model.make_future_dataframe(periods=request.horizon_days)
    forecast_df = prophet_model.predict(future)

    # Only return the newly predicted rows, not the historical fit
    future_only = forecast_df.tail(request.horizon_days)

    points = [
        ForecastPoint(
            date=row["ds"].strftime("%Y-%m-%d"),
            predicted_demand=round(row["yhat"], 2),
            lower_bound=round(row["yhat_lower"], 2),
            upper_bound=round(row["yhat_upper"], 2),
        )
        for _, row in future_only.iterrows()
    ]

    return ForecastResponse(horizon_days=request.horizon_days, forecast=points)