import streamlit as st
import requests
import json

st.set_page_config(page_title="Dubai Real Estate Price Predictor", page_icon="🏙️", layout="wide")

with open("dropdown_values.json") as f:
    options = json.load(f)

API_URL = "https://dubai-real-estate-predictor.onrender.com/predict"

st.title("🏙️ Dubai Real Estate Price Predictor")
st.write("Estimate a Dubai property's resale price using a trained XGBoost model (R² = 0.99).")

with st.expander("ℹ️ About this model"):
    st.write(
        "Trained on 50,000 real Dubai secondary market transactions (2020–2026). "
        "Compared Linear Regression, Random Forest, and XGBoost — XGBoost performed best "
        "with a median prediction error of roughly $36,700. Location (community) is the "
        "single strongest price driver, followed by property size."
    )

st.subheader("Try an example")
preset_col1, preset_col2, preset_col3 = st.columns(3)
preset = None
if preset_col1.button("🏢 Karama Apartment"):
    preset = "karama"
if preset_col2.button("🏙️ DIFC Penthouse"):
    preset = "difc"
if preset_col3.button("🏡 Emirates Hills Villa"):
    preset = "emirates_hills"

presets = {
    "karama": dict(community="Karama", zone="Bur Dubai", property_category="apartment",
                   property_type="1BR", bedrooms=1, area_sqft=824, area_m2=76.5, floor=14,
                   total_floors=30, year_built=2012, view="park", furnishing="unfurnished",
                   condition="tenanted", parking_spaces=2, chiller_included=False,
                   metro_station="BurJuman (G)", metro_line="Green", metro_distance_min=14,
                   metro_distance_type="walk", to_burj_khalifa_km=6.05,
                   mortgage_rate_at_listing=1.90, listing_year=2022, listing_month=1,
                   lat=25.24835, lon=55.29501, is_freehold=False),
    "difc": dict(community="DIFC", zone="DIFC", property_category="apartment",
                 property_type="4BR_penthouse", bedrooms=4, area_sqft=3658, area_m2=339.9,
                 floor=11, total_floors=20, year_built=2021, view="burj_khalifa",
                 furnishing="unfurnished", condition="vacant_on_transfer", parking_spaces=2,
                 chiller_included=True, metro_station="Financial Centre", metro_line="Red",
                 metro_distance_min=6, metro_distance_type="walk", to_burj_khalifa_km=2.51,
                 mortgage_rate_at_listing=6.15, listing_year=2024, listing_month=11,
                 lat=25.21053, lon=55.29453, is_freehold=True),
    "emirates_hills": dict(community="Emirates Hills", zone="Emirates Hills", property_category="villa",
                            property_type="5BR_villa", bedrooms=5, area_sqft=8500, area_m2=789.7,
                            floor=0, total_floors=0, year_built=2015, view="golf_course",
                            furnishing="unfurnished", condition="vacant_on_transfer", parking_spaces=4,
                            chiller_included=True, metro_station="Financial Centre", metro_line="Red",
                            metro_distance_min=25, metro_distance_type="drive", to_burj_khalifa_km=15.0,
                            mortgage_rate_at_listing=4.5, listing_year=2023, listing_month=6,
                            lat=25.0657, lon=55.1713, is_freehold=True),
}

d = presets.get(preset, {})

st.divider()

with st.form("predict_form"):
    col1, col2 = st.columns(2)

    with col1:
        community = st.selectbox("Community", options["community"],
                                  index=options["community"].index(d["community"]) if d else 0)
        zone = st.selectbox("Zone", options["zone"],
                             index=options["zone"].index(d["zone"]) if d else 0)
        property_category = st.selectbox("Property Category", options["property_category"],
                                          index=options["property_category"].index(d["property_category"]) if d else 0)
        property_type = st.selectbox("Property Type", options["property_type"],
                                      index=options["property_type"].index(d["property_type"]) if d else 0)
        bedrooms = st.number_input("Bedrooms", min_value=0, value=d.get("bedrooms", 1))
        area_sqft = st.number_input("Area (sqft)", min_value=0, value=d.get("area_sqft", 800))
        area_m2 = st.number_input("Area (m²)", min_value=0.0, value=d.get("area_m2", 74.3))
        floor = st.number_input("Floor (0 if villa)", min_value=0, value=d.get("floor", 0))
        total_floors = st.number_input("Total Floors (0 if villa)", min_value=0, value=d.get("total_floors", 0))
        year_built = st.number_input("Year Built", min_value=1950, max_value=2026, value=d.get("year_built", 2018))
        view = st.selectbox("View", options["view"],
                             index=options["view"].index(d["view"]) if d else 0)
        is_freehold = st.checkbox("Freehold", value=d.get("is_freehold", False))

    with col2:
        furnishing = st.selectbox("Furnishing", options["furnishing"],
                                   index=options["furnishing"].index(d["furnishing"]) if d else 0)
        condition = st.selectbox("Condition", options["condition"],
                                  index=options["condition"].index(d["condition"]) if d else 0)
        parking_spaces = st.number_input("Parking Spaces", min_value=0, value=d.get("parking_spaces", 1))
        chiller_included = st.checkbox("Chiller Included", value=d.get("chiller_included", False))
        metro_station = st.selectbox("Metro Station", options["metro_station"],
                                      index=options["metro_station"].index(d["metro_station"]) if d else 0)
        metro_line = st.selectbox("Metro Line", options["metro_line"],
                                   index=options["metro_line"].index(d["metro_line"]) if d else 0)
        metro_distance_min = st.number_input("Metro Distance (min)", min_value=0, value=d.get("metro_distance_min", 10))
        metro_distance_type = st.selectbox("Metro Distance Type", options["metro_distance_type"],
                                            index=options["metro_distance_type"].index(d["metro_distance_type"]) if d else 0)
        to_burj_khalifa_km = st.number_input("Distance to Burj Khalifa (km)", min_value=0.0, value=d.get("to_burj_khalifa_km", 10.0))
        mortgage_rate_at_listing = st.number_input("Mortgage Rate at Listing (%)", min_value=0.0, value=d.get("mortgage_rate_at_listing", 4.0))
        listing_year = st.number_input("Listing Year", min_value=2015, max_value=2026, value=d.get("listing_year", 2024))
        listing_month = st.number_input("Listing Month", min_value=1, max_value=12, value=d.get("listing_month", 6))
        lat = st.number_input("Latitude", value=d.get("lat", 25.2048), format="%.5f")
        lon = st.number_input("Longitude", value=d.get("lon", 55.2708), format="%.5f")

    submitted = st.form_submit_button("🔮 Predict Price", type="primary", use_container_width=True)

if submitted:
    payload = dict(
        community=community, zone=zone, is_freehold=is_freehold, lat=lat, lon=lon,
        property_category=property_category, property_type=property_type, bedrooms=bedrooms,
        area_sqft=area_sqft, area_m2=area_m2, floor=floor, total_floors=total_floors,
        year_built=year_built, view=view, furnishing=furnishing, condition=condition,
        parking_spaces=parking_spaces, chiller_included=chiller_included,
        metro_station=metro_station, metro_line=metro_line, metro_distance_min=metro_distance_min,
        metro_distance_type=metro_distance_type, to_burj_khalifa_km=to_burj_khalifa_km,
        mortgage_rate_at_listing=mortgage_rate_at_listing, listing_year=listing_year,
        listing_month=listing_month
    )

    with st.spinner("Running prediction... (first request may take ~30s if the API was asleep)"):
        try:
            response = requests.post(API_URL, json=payload, timeout=60)
            if response.status_code == 200:
                price = response.json()["predicted_price_usd"]
                st.success("Prediction complete")
                st.metric("Estimated Price (USD)", f"${price:,.0f}")
                st.map({"lat": [lat], "lon": [lon]}, zoom=11)
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the API: {e}")

st.divider()
st.caption("Built by Alaa · [View source on GitHub](https://github.com/Alaa-elden-mohammed/Dubai-real-estate-predictor)")