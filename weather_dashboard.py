import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

# --- CONFIGURATION ---
# REPLACE "YOUR_API_KEY_HERE" with your actual OpenWeatherMap API key.
API_KEY = "68788ff9118d4b67b824f7de14c13cd6"
BASE_URL = "http://api.openweathermap.org/data/2.5/forecast"


def get_weather_data(city_name):
    """
    Fetches weather data. If the API fails (e.g., key not active yet),
    it generates SIMULATED data so the project still runs for testing.
    """
    try:
        # 1. Try to get REAL data
        params = {
            'q': city_name,
            'appid': API_KEY,
            'units': 'metric'
        }
        response = requests.get(BASE_URL, params=params)

        # If the API returns success (200), return the real JSON
        if response.status_code == 200:
            return response.json()

        # 2. If API fails (e.g., Key not active), generate FAKE data
        # This ensures you can demonstrate the project even if the API is down
        st.warning(f"⚠️ API Key issue (Code {response.status_code}). Switching to SIMULATION MODE for {city_name}.")

        fake_data = {"list": []}
        current_time = datetime.now()

        # Generate 40 data points (5 days * 8 intervals of 3 hours)
        for i in range(40):
            future_time = current_time + timedelta(hours=3 * i)

            # Create a realistic temperature pattern
            hour = future_time.hour
            base_temp = 25  # Average temp

            # Hotter in afternoon, cooler at night
            if 0 <= hour < 6:
                temp = base_temp - 5 + random.uniform(-1, 1)  # Night
            elif 12 <= hour < 16:
                temp = base_temp + 5 + random.uniform(-1, 1)  # Afternoon
            else:
                temp = base_temp + random.uniform(-2, 2)  # Evening

            fake_entry = {
                "dt_txt": future_time.strftime("%Y-%m-%d %H:%M:%S"),
                "main": {"temp": round(temp, 2)}
            }
            fake_data["list"].append(fake_entry)

        return fake_data

    except Exception as e:
        st.error(f"❌ Critical Error: {e}")
        return None


def process_weather_data(data):
    """
    Processes the raw JSON data into a clean Pandas DataFrame.
    """
    forecast_list = data['list']

    dates = []
    temps = []

    for item in forecast_list:
        dt_txt = item['dt_txt']
        temp = item['main']['temp']
        dates.append(dt_txt)
        temps.append(temp)

    # Create DataFrame
    df = pd.DataFrame({
        "Date": pd.to_datetime(dates),
        "Temperature": temps
    })
    return df


# --- MAIN APP UI ---

st.set_page_config(page_title="Weather Dashboard", page_icon="⛅")

st.title("⛅ Live Weather Forecast Dashboard")
st.markdown("""
**Project Domain:** Visualizations & APIs  
This tool fetches 5-day weather forecasts and visualizes trends using **Matplotlib**.
""")

st.write("---")

# User Input
city = st.text_input("Enter City Name:", placeholder="e.g., Bangalore, Mysore, Delhi")

if city:
    with st.spinner('Fetching data...'):
        raw_data = get_weather_data(city)

    if raw_data:
        df = process_weather_data(raw_data)

        # Current Temp Display
        current_temp = df['Temperature'].iloc[0]
        st.success(f"Weather Forecast for **{city.title()}**")
        st.metric(label="Current Temperature", value=f"{current_temp}°C")

        # --- VISUALIZATION ---
        st.subheader("Temperature Trend (Next 5 Days)")

        fig, ax = plt.subplots(figsize=(10, 5))

        # Plot Data
        ax.plot(df['Date'], df['Temperature'], marker='o', linestyle='-', color='tab:blue')

        # Formatting
        ax.set_title(f"Temperature vs Time for {city.title()}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Temp (°C)")
        ax.grid(True, linestyle='--', alpha=0.5)
        plt.xticks(rotation=45)

        # Show Plot
        st.pyplot(fig)

        # Show Data Table
        with st.expander("View Raw Data"):
            st.dataframe(df)

st.write("---")
st.caption("Python Mini Project | Created with Streamlit")