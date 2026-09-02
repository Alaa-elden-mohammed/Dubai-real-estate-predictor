import streamlit as st
import requests

st.set_page_config(page_title="Dubai Real Estate Price Predictor", page_icon="🏙️")
st.title("🏙️ Dubai Real Estate Price Predictor")
st.write("Estimate a property's resale price based on its features.")

API_URL = "https://dubai-real-estate-predictor.onrender.com/predict"

col1, col2 = st.columns(2)

with col1:
    community = st.text_input("Community", "Karama")
    zone = st.text_input("Zone", "Bur Dubai")
    property_category = st.selectbox("Property Category", ["apartment", "villa"])
    property_type = st.text_input("Property Type", "1BR")
    bedrooms = st.number_input("Bedrooms", min_value=0, value=1)
    area_sqft = st.number_input("Area (sqft)", min_value=0, value=824)
    area_m2 = st.number_input("Area (m²)", min_value=0.0, value=76.5)
    floor = st.number_input("Floor", min_value=0, value=14)
    total_floors = st.number_input("Total Floors", min_value=0, value=30)
    year_built = st.number_input("Year Built", min_value=1950, max_value=2026, value=2012)
    view = st.text_input("View", "park")
    is_freehold = st.checkbox("Freehold", value=False)

with col2:
    furnishing = st.selectbox("Furnishing", ["unfurnished", "furnished", "semi_furnished"])
    condition = st.text_input("Condition", "tenanted")
    parking_spaces = st.number_input("Parking Spaces", min_value=0, value=2)
    chiller_included = st.checkbox("Chiller Included", value=False)
    metro_station = st.text_input("Metro Station", "BurJuman (G)")
    metro_line = st.text_input("Metro Line", "Green")
    metro_distance_min = st.number_input("Metro Distance (min)", min_value=0, value=14)
    metro_distance_type = st.selectbox("Metro Distance Type", ["walk", "drive"])
    to_burj_khalifa_km = st.number_input("Distance to Burj Khalifa (km)", min_value=0.0, value=6.05)
    mortgage_rate_at_listing = st.number_input("Mortgage Rate at Listing (%)", min_value=0.0, value=1.90)
    listing_year = st.number_input("Listing Year", min_value=2015, max_value=2026, value=2022)
    listing_month = st.number_input("Listing Month", min_value=1, max_value=12, value=1)
    lat = st.number_input("Latitude", value=25.24835, format="%.5f")
    lon = st.number_input("Longitude", value=55.29501, format="%.5f")

if st.button("Predict Price", type="primary"):
    payload = {
        "community": community, "zone": zone, "is_freehold": is_freehold,
        "lat": lat, "lon": lon, "property_category": property_category,
        "property_type": property_type, "bedrooms": bedrooms, "area_sqft": area_sqft,
        "area_m2": area_m2, "floor": floor, "total_floors": total_floors,
        "year_built": year_built, "view": view, "furnishing": furnishing,
        "condition": condition, "parking_spaces": parking_spaces,
        "chiller_included": chiller_included, "metro_station": metro_station,
        "metro_line": metro_line, "metro_distance_min": metro_distance_min,
        "metro_distance_type": metro_distance_type, "to_burj_khalifa_km": to_burj_khalifa_km,
        "mortgage_rate_at_listing": mortgage_rate_at_listing,
        "listing_year": listing_year, "listing_month": listing_month
    }
    with st.spinner("Contacting model... (may take ~30s if the API was asleep)"):
        response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        price = response.json()["predicted_price_usd"]
        st.success(f"Estimated Price: **${price:,.2f}**")
    else:
        st.error(f"Error: {response.status_code} — {response.text}")