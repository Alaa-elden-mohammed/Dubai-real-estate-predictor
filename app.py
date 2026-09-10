import streamlit as st
import requests
import json
import plotly.graph_objects as go

st.set_page_config(page_title="Dubai Real Estate Price Predictor", page_icon="🏙️", layout="wide")

AED_PEG = 3.6725
API_URL = "https://dubai-real-estate-predictor.onrender.com/predict"
ACCENT, NEUTRAL = "#4F8BF9", "#4A4E58"

@st.cache_data
def load_assets():
    with open("dropdown_values.json") as f:
        options = json.load(f)
    with open("community_avg_price.json") as f:
        avg_prices = json.load(f)
    with open("feature_importance.json") as f:
        feat_imp = json.load(f)
    return options, avg_prices, feat_imp

options, community_avg_price, feature_importance = load_assets()

def get_index(option_list, val, default=0):
    try:
        return option_list.index(val)
    except (ValueError, KeyError, TypeError):
        return default

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

if "current_preset" not in st.session_state:
    st.session_state.current_preset = presets["karama"]

st.title("🏙️ Dubai Real Estate Price Predictor")
st.caption("Trained on 50,000 real Dubai secondary-market transactions · XGBoost · R² = 0.99")

tab_predict, tab_explore, tab_about = st.tabs(["🔮 Predict", "📊 Explore Data", "ℹ️ About"])

with tab_predict:
    st.subheader("Try an Example")
    p_cols = st.columns(3)
    if p_cols[0].button("🏢 Karama Apartment", use_container_width=True):
        st.session_state.current_preset = presets["karama"]
        st.rerun()
    if p_cols[1].button("🏙️ DIFC Penthouse", use_container_width=True):
        st.session_state.current_preset = presets["difc"]
        st.rerun()
    if p_cols[2].button("🏡 Emirates Hills Villa", use_container_width=True):
        st.session_state.current_preset = presets["emirates_hills"]
        st.rerun()

    data = st.session_state.current_preset
    st.divider()

    with st.form("predict_form"):
        col1, col2 = st.columns(2)

        with col1:
            community = st.selectbox("Community", options["community"],
                                     index=get_index(options["community"], data.get("community")))
            zone = st.selectbox("Zone", options["zone"],
                                index=get_index(options["zone"], data.get("zone")))
            property_category = st.selectbox("Category", options["property_category"],
                                             index=get_index(options["property_category"], data.get("property_category")))
            property_type = st.selectbox("Unit Type", options["property_type"],
                                         index=get_index(options["property_type"], data.get("property_type")))
            bedrooms = st.slider("Bedrooms", 0, 10, data.get("bedrooms", 1))
            area_sqft = st.slider("Area (sqft)", 200, 10000, data.get("area_sqft", 800), step=50)
            area_m2 = round(area_sqft * 0.092903, 1)
            st.caption(f"≈ {area_m2} m²")

            floor = st.number_input("Floor (set 0 for villas)", min_value=0, value=data.get("floor", 0))
            total_floors = st.number_input("Total Floors in Building (set 0 for villas)", min_value=0, value=data.get("total_floors", 0))
            year_built = st.slider("Year Built", 1990, 2026, data.get("year_built", 2018))

        with col2:
            view = st.selectbox("View", options["view"], index=get_index(options["view"], data.get("view")))
            furnishing = st.selectbox("Furnishing", options["furnishing"], index=get_index(options["furnishing"], data.get("furnishing")))
            condition = st.selectbox("Condition", options["condition"], index=get_index(options["condition"], data.get("condition")))
            parking_spaces = st.slider("Parking Spaces", 0, 6, data.get("parking_spaces", 1))
            is_freehold = st.checkbox("Freehold", value=data.get("is_freehold", True))
            chiller_included = st.checkbox("Chiller Included", value=data.get("chiller_included", False))

        with st.expander("Advanced: Location, Metro & Market Assumptions"):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                lat = st.number_input("Latitude", value=data.get("lat", 25.2048), format="%.5f")
                lon = st.number_input("Longitude", value=data.get("lon", 55.2708), format="%.5f")
                metro_station = st.selectbox("Metro Station", options["metro_station"],
                                             index=get_index(options["metro_station"], data.get("metro_station")))
                metro_line = st.selectbox("Metro Line", options["metro_line"],
                                          index=get_index(options["metro_line"], data.get("metro_line")))
                metro_distance_min = st.slider("Metro Distance (min)", 0, 60, data.get("metro_distance_min", 10))
                metro_distance_type = st.selectbox("Metro Distance Type", options["metro_distance_type"],
                                                    index=get_index(options["metro_distance_type"], data.get("metro_distance_type")))
            with col_m2:
                to_burj_khalifa_km = st.slider("Distance to Burj Khalifa (km)", 0.0, 50.0, data.get("to_burj_khalifa_km", 10.0))
                mortgage_rate_at_listing = st.slider("Mortgage Rate at Listing (%)", 1.0, 10.0, data.get("mortgage_rate_at_listing", 4.5))
                listing_year = st.number_input("Listing Year", 2015, 2026, data.get("listing_year", 2024))
                listing_month = st.slider("Listing Month", 1, 12, data.get("listing_month", 6))

        submitted = st.form_submit_button("🔮 Predict Valuation", type="primary", use_container_width=True)

    if submitted:
        # Sanitize floors if property is villa
        final_floor = 0 if property_category.lower() != "apartment" else floor
        final_total_floors = 0 if property_category.lower() != "apartment" else total_floors

        payload = dict(
            community=community, zone=zone, is_freehold=is_freehold, lat=lat, lon=lon,
            property_category=property_category, property_type=property_type, bedrooms=bedrooms,
            area_sqft=area_sqft, area_m2=area_m2, floor=final_floor, total_floors=final_total_floors,
            year_built=year_built, view=view, furnishing=furnishing, condition=condition,
            parking_spaces=parking_spaces, chiller_included=chiller_included,
            metro_station=metro_station, metro_line=metro_line, metro_distance_min=metro_distance_min,
            metro_distance_type=metro_distance_type, to_burj_khalifa_km=to_burj_khalifa_km,
            mortgage_rate_at_listing=mortgage_rate_at_listing, listing_year=listing_year,
            listing_month=listing_month
        )

        with st.status("Calculating valuation...", expanded=True) as status:
            st.write("Connecting to server (free-tier instances may require ~45s to wake)...")
            try:
                response = requests.post(API_URL, json=payload, timeout=90)
                if response.status_code == 200:
                    price = response.json()["predicted_price_usd"]
                    st.session_state.last_prediction = {
                        "price": price,
                        "payload": payload
                    }
                    status.update(label="Valuation complete!", state="complete", expanded=False)
                else:
                    status.update(label=f"API Error {response.status_code}", state="error", expanded=True)
                    st.error(f"Response: {response.text}")
            except requests.exceptions.RequestException as e:
                status.update(label="Connection Failed", state="error", expanded=True)
                st.error(f"Could not reach API: {e}")

    # Render results (persists across tab switches)
    if "last_prediction" in st.session_state:
        pred_data = st.session_state.last_prediction
        price = pred_data["price"]
        p_load = pred_data["payload"]
        price_aed = price * AED_PEG

        st.divider()
        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.metric("Estimated Price (AED)", f"AED {price_aed:,.0f}")
            st.metric("Estimated Price (USD)", f"${price:,.0f}")
            st.metric("Price / sq. ft. (AED)", f"AED {price_aed/p_load['area_sqft']:,.0f}")
            st.metric("Price / sq. ft. (USD)", f"${price/p_load['area_sqft']:,.0f}")

        with col_b:
            map_fig = go.Figure(go.Scattermap(
                lat=[p_load["lat"]], lon=[p_load["lon"]], mode='markers',
                marker=dict(size=16, color=ACCENT),
                text=[p_load["community"]], hoverinfo='text'
            ))
            map_fig.update_layout(
                map_style="carto-positron",
                map=dict(center=dict(lat=p_load["lat"], lon=p_load["lon"]), zoom=11),
                height=350,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            st.plotly_chart(map_fig, use_container_width=True)

        avg_price = community_avg_price.get(p_load["community"])
        if avg_price:
            fig = go.Figure(data=[
                go.Bar(name="This Property", x=["Price"], y=[price], marker_color=ACCENT),
                go.Bar(name=f"{p_load['community']} Average", x=["Price"], y=[avg_price], marker_color=NEUTRAL),
            ])
            fig.update_layout(title=f"Prediction vs. {p_load['community']} Average", barmode="group", height=350)
            st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure(go.Bar(
            x=feature_importance["values"][::-1],
            y=feature_importance["labels"][::-1],
            orientation="h",
            marker_color=ACCENT
        ))
        fig2.update_layout(title="Overall Dataset Feature Importance", height=350)
        st.plotly_chart(fig2, use_container_width=True)

with tab_explore:
    st.subheader("Average Price by Community (Top 15)")
    sorted_communities = dict(sorted(community_avg_price.items(), key=lambda x: x[1], reverse=True)[:15])
    fig3 = go.Figure(go.Bar(
        x=list(sorted_communities.values()),
        y=list(sorted_communities.keys()),
        orientation="h",
        marker_color=ACCENT
    ))
    fig3.update_layout(height=500, xaxis_title="Average Price (USD)")
    st.plotly_chart(fig3, use_container_width=True)

with tab_about:
    st.subheader("About this project")
    st.write(
        "This model was trained on 50,000 real Dubai secondary-market property transactions "
        "(2020–2026). Three models were compared — Linear Regression, Random Forest, and XGBoost — "
        "with XGBoost performing best (R² = 0.99, median error ≈ $36,700)."
    )
    st.write(
        "Community/location is the single strongest price driver, followed by property size. "
        "The full pipeline — data cleaning, feature engineering, model training, and this live "
        "demo — is documented in the GitHub repository."
    )
    st.link_button("View source on GitHub", "https://github.com/Alaa-elden-mohammed/Dubai-real-estate-predictor")

st.divider()
st.caption("Built by Alaa · Free-tier hosting on Render + Streamlit Community Cloud")