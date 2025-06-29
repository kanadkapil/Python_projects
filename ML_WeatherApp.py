import streamlit as st
import pandas as pd
import requests
from prophet import Prophet
from datetime import datetime, timedelta

city = st.sidebar.text_input("City", "New York")

city_coords = {
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "Dhaka": (23.8103, 90.4125),
    "Tokyo": (35.6762, 139.6503)
}

if city not in city_coords:
    st.error("City not supported. Please choose from: " + ", ".join(city_coords.keys()))
    st.stop()

lat, lon = city_coords[city]

# Fix here: convert today to pandas Timestamp
today = pd.Timestamp(datetime.utcnow().date())
start_date = today - timedelta(days=10)
end_date = today + timedelta(days=10)

url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={lat}&longitude={lon}"
    f"&start_date={start_date.date()}&end_date={end_date.date()}"
    f"&daily=temperature_2m_max,temperature_2m_min"
    f"&timezone=UTC"
)

response = requests.get(url)
data = response.json()

if "daily" not in data:
    st.error("Failed to get weather data.")
    st.stop()

dates = data["daily"]["time"]
temps_max = data["daily"]["temperature_2m_max"]
temps_min = data["daily"]["temperature_2m_min"]

df = pd.DataFrame({
    "ds": pd.to_datetime(dates),
    "y": [(max_t + min_t) / 2 for max_t, min_t in zip(temps_max, temps_min)]
})

historical_df = df[df["ds"] <= today]
future_df = df[df["ds"] > today]

m = Prophet()
m.fit(historical_df)

future = m.make_future_dataframe(periods=10)
forecast = m.predict(future)

st.subheader(f"Last 10 days actual temperature in {city}")
st.line_chart(historical_df.set_index("ds")["y"])

st.subheader(f"Next 10 days forecast temperature in {city}")
st.line_chart(forecast.set_index("ds")["yhat"])

st.write(m.plot_components(forecast))
