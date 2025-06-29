import streamlit as st
import pandas as pd
import requests
from prophet import Prophet
from datetime import datetime, timedelta


city_coords = {
    # --- India ---
    "Mumbai, India": (19.0760, 72.8777),
    "Delhi, India": (28.6139, 77.2090),
    "Bengaluru, India": (12.9716, 77.5946),
    "Kolkata, India": (22.5726, 88.3639),
    "Chennai, India": (13.0827, 80.2707),
    "Hyderabad, India": (17.3850, 78.4867),
    "Pune, India": (18.5204, 73.8567),
    "Ahmedabad, India": (23.0225, 72.5714),
    "Jaipur, India": (26.9124, 75.7873),
    "Lucknow, India": (26.8467, 80.9462),

    # --- Bangladesh ---
    "Dhaka, Bangladesh": (23.8103, 90.4125),
    "Chittagong, Bangladesh": (22.3569, 91.7832),
    "Khulna, Bangladesh": (22.8456, 89.5403),
    "Rajshahi, Bangladesh": (24.3636, 88.6241),
    "Sylhet, Bangladesh": (24.8949, 91.8687),

    # --- United States ---
    "New York, USA": (40.7128, -74.0060),
    "Los Angeles, USA": (34.0522, -118.2437),
    "Chicago, USA": (41.8781, -87.6298),
    "Houston, USA": (29.7604, -95.3698),
    "Phoenix, USA": (33.4484, -112.0740),
    "Philadelphia, USA": (39.9526, -75.1652),
    "San Antonio, USA": (29.4241, -98.4936),
    "San Diego, USA": (32.7157, -117.1611),
    "Dallas, USA": (32.7767, -96.7970),
    "San Francisco, USA": (37.7749, -122.4194),

    # --- Australia ---
    "Sydney, Australia": (-33.8688, 151.2093),
    "Melbourne, Australia": (-37.8136, 144.9631),
    "Brisbane, Australia": (-27.4698, 153.0251),
    "Perth, Australia": (-31.9505, 115.8605),
    "Adelaide, Australia": (-34.9285, 138.6007),
    "Canberra, Australia": (-35.2809, 149.1300),

    # --- Europe ---
    "London, UK": (51.5074, -0.1278),
    "Paris, France": (48.8566, 2.3522),
    "Berlin, Germany": (52.5200, 13.4050),
    "Madrid, Spain": (40.4168, -3.7038),
    "Rome, Italy": (41.9028, 12.4964),
    "Amsterdam, Netherlands": (52.3676, 4.9041),
    "Vienna, Austria": (48.2082, 16.3738),
    "Zurich, Switzerland": (47.3769, 8.5417),
    "Stockholm, Sweden": (59.3293, 18.0686),
    "Copenhagen, Denmark": (55.6761, 12.5683),
    "Oslo, Norway": (59.9139, 10.7522),
    "Helsinki, Finland": (60.1695, 24.9354),
    "Dublin, Ireland": (53.3498, -6.2603),
    "Brussels, Belgium": (50.8503, 4.3517),
    "Lisbon, Portugal": (38.7169, -9.1399),
    "Warsaw, Poland": (52.2297, 21.0122),
    "Prague, Czech Republic": (50.0755, 14.4378),
    "Budapest, Hungary": (47.4979, 19.0402),
    "Athens, Greece": (37.9838, 23.7275),

    # --- Other Global Cities ---
    "Tokyo, Japan": (35.6762, 139.6503),
    "Seoul, South Korea": (37.5665, 126.9780),
    "Beijing, China": (39.9042, 116.4074),
    "Shanghai, China": (31.2304, 121.4737),
    "Moscow, Russia": (55.7558, 37.6173),
    "Singapore, Singapore": (1.3521, 103.8198),
    "Dubai, UAE": (25.2048, 55.2708),
    "Cape Town, South Africa": (-33.9249, 18.4241),
    "Toronto, Canada": (43.6532, -79.3832),
    "Buenos Aires, Argentina": (-34.6037, -58.3816),
    "Mexico City, Mexico": (19.4326, -99.1332),
    "Sao Paulo, Brazil": (-23.5505, -46.6333),
}


st.set_page_config(layout="wide") # Use wide layout for better visualization

st.title("Weather Forecast Application")

city = st.sidebar.selectbox("Select a city", list(city_coords.keys()))

if city not in city_coords:
    st.error("City not supported. Please choose from: " + ", ".join(city_coords.keys()))
    st.stop()

lat, lon = city_coords[city]

today = pd.Timestamp(datetime.utcnow().date())
start_date = today - timedelta(days=10)
end_date = today + timedelta(days=10)

# Add precipitation_probability_max and weathercode for day type
url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={lat}&longitude={lon}"
    f"&start_date={start_date.date()}&end_date={end_date.date()}"
    f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode"
    f"&timezone=UTC"
)

response = requests.get(url)
data = response.json()

if "daily" not in data:
    st.error("Failed to get weather data. Please try again later.")
    st.stop()

dates = data["daily"]["time"]
temps_max = data["daily"]["temperature_2m_max"]
temps_min = data["daily"]["temperature_2m_min"]
precip_prob = data["daily"].get("precipitation_probability_max", [0]*len(dates))  # fallback zeros
weathercodes = data["daily"].get("weathercode", [0]*len(dates))  # fallback zeros

df = pd.DataFrame({
    "ds": pd.to_datetime(dates),
    "temp_avg": [(max_t + min_t) / 2 for max_t, min_t in zip(temps_max, temps_min)],
    "temp_max": temps_max,
    "temp_min": temps_min,
    "precip_prob": precip_prob,
    "weathercode": weathercodes
})

historical_df = df[df["ds"] <= today].copy() # Use .copy() to avoid SettingWithCopyWarning
future_df = df[df["ds"] > today].copy() # Use .copy()

# Train Prophet on historical data only
m = Prophet()
m.fit(historical_df.rename(columns={"temp_avg": "y"}))

# Create a future dataframe for 10 days from today
future = m.make_future_dataframe(periods=10)
forecast = m.predict(future)

# Separate forecast into historical and future parts for plotting
forecast_historical = forecast[forecast["ds"] <= today]
forecast_future = forecast[forecast["ds"] > today]

st.subheader(f"Temperature Trends for {city}")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Past 10 Days (Actual Temperature)")
    st.line_chart(historical_df.set_index("ds")["temp_avg"])

with col2:
    st.markdown("#### Next 10 Days (Forecasted Average Temperature)")
    # We only want to plot the future part of the forecast
    st.line_chart(forecast_future.set_index("ds")["yhat"])

st.subheader("Forecast Components")
st.write(m.plot_components(forecast))

# --- Next Day Weather Details ---

next_day = today + timedelta(days=1)
next_day_data = df[df["ds"] == next_day]

if not next_day_data.empty:
    next_day_data = next_day_data.iloc[0]

    st.subheader(f"Detailed Weather for {next_day.date()} in {city}")

    # Display table with next day weather info
    weather_data_for_table = {
        "Metric": [
            "Max Temperature (°C)",
            "Min Temperature (°C)",
            "Average Temperature (°C)",
            "Rain Probability (%)"
        ],
        "Value": [
            next_day_data.temp_max,
            next_day_data.temp_min,
            next_day_data.temp_avg,
            next_day_data.precip_prob
        ]
    }
    weather_df = pd.DataFrame(weather_data_for_table)

    # Apply color gradients for better visual cue
    # We need to apply the gradients to the 'Value' column
    styled_weather_df = weather_df.style.background_gradient(
        cmap='coolwarm', subset=pd.IndexSlice[[0, 1, 2], "Value"]
    ).background_gradient(
        cmap='Blues', subset=pd.IndexSlice[[3], "Value"]
    )

    st.dataframe(styled_weather_df, use_container_width=True)

    # Map weathercode to description
    weather_code_map = {
        0: "Clear sky (Sunny) ☀️",
        1: "Mainly clear 🌤️",
        2: "Partly cloudy (Gloomy) ⛅",
        3: "Overcast ☁️",
        45: "Fog 🌫️",
        48: "Depositing rime fog 🌫️❄️",
        51: "Light drizzle (Sprinkles) 🌦️",
        53: "Moderate drizzle 🌦️",
        55: "Dense drizzle 🌧️",
        56: "Light freezing drizzle 🌧️❄️",
        57: "Dense freezing drizzle 🌧️❄️",
        61: "Slight rain (Sprinkles) 🌦️",
        63: "Moderate rain 🌧️",
        65: "Heavy rain 🌧️💧",
        66: "Light freezing rain ❄️🌧️",
        67: "Heavy freezing rain ❄️🌧️",
        71: "Slight snow 🌨️",
        73: "Moderate snow 🌨️❄️",
        75: "Heavy snow 🌨️⛄",
        77: "Snow grains 🌨️",
        80: "Slight rain showers (Sprinkles) 🌦️",
        81: "Moderate rain showers 🌧️",
        82: "Violent rain showers ⛈️",
        85: "Slight snow showers 🌨️",
        86: "Heavy snow showers ❄️🌨️",
        95: "Thunderstorm (Thunderstorms) ⛈️",
        96: "Thunderstorm with slight hail ⛈️🌨️",
        99: "Thunderstorm with heavy hail ⛈️🌨️❄️",
    }

    day_type = weather_code_map.get(next_day_data.weathercode, "Unknown")
    st.markdown(f"**Day type:** {day_type}")

    # Optional: Plot next day temperature point on graph (might be redundant with table)
    # st.line_chart(pd.DataFrame({
    #     "Temperature": [next_day_data.temp_avg]
    # }, index=[next_day]))

else:
    st.warning("No weather data available for the next day.")
