
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np

app = FastAPI(title="Dubai Real Estate Price Predictor")

model = joblib.load("models/xgb_model.pkl")
community_map = joblib.load("models/community_map.pkl")
zone_map = joblib.load("models/zone_map.pkl")
metro_map = joblib.load("models/metro_map.pkl")
feature_columns = joblib.load("models/feature_columns.pkl")

class PropertyInput(BaseModel):
    community: str
    zone: str
    is_freehold: bool
    lat: float
    lon: float
    property_category: str
    property_type: str
    bedrooms: int
    area_sqft: int
    area_m2: float
    floor: float
    total_floors: float
    year_built: int
    view: str
    furnishing: str
    condition: str
    parking_spaces: int
    chiller_included: bool
    metro_station: str
    metro_line: str
    metro_distance_min: int
    metro_distance_type: str
    to_burj_khalifa_km: float
    mortgage_rate_at_listing: float
    listing_year: int
    listing_month: int

@app.post("/predict")
def predict(data: PropertyInput):
    row = data.dict()

    row["community_encoded"] = community_map.get(row.pop("community"), community_map.mean())
    row["zone_encoded"] = zone_map.get(row.pop("zone"), zone_map.mean())
    row["metro_station_encoded"] = metro_map.get(row.pop("metro_station"), metro_map.mean())
    row["has_floor_info"] = 1 if row["floor"] > 0 else 0

    df_input = pd.DataFrame([row])
    df_input = pd.get_dummies(df_input)
    df_input = df_input.reindex(columns=feature_columns, fill_value=0)

    pred_log = model.predict(df_input)[0]
    pred_price = float(np.expm1(pred_log))

    return {"predicted_price_usd": round(pred_price, 2)}
