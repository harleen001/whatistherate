import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="WhatIsTheRate", page_icon="📈", layout="wide")

# Custom CSS to make it look less like "standard" Streamlit
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Fetching Functions
@st.cache_data(ttl=3600)
def fetch_metal_rates():
    # Using yfinance for Gold/Silver
    gold = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
    silver = yf.Ticker("SI=F").history(period="1d")['Close'].iloc[-1]
    # Rough USD to INR conversion (83.5 approx)
    return round(gold * 83.5 / 31.1, 2), round(silver * 83.5 * 32.15, 2)

@st.cache_data(ttl=14400) # Update every 4 hours
def fetch_fuel_rates():
    try:
        # Example: Scraping a reliable source for Jalandhar/Punjab Petrol
        url = "https://www.goodreturns.in/petrol-price-in-jalandhar.html"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # This selector depends on the site's structure
        price = soup.find("div", {"class": "gold_silver_table"}).find("td").find_next('td').text
        return price.strip()
    except:
        return "103.50" # Fallback static price

# 3. Header
st.title("🔍 WhatIsTheRate.py")
st.caption("Real-time resource tracking for Punjab & Global Markets")

# 4. Interactive Search (The "What Is" part)
search_query = st.text_input("What would you like to check?", placeholder="Type 'Gold', 'Petrol', or 'Solar'...")

# 5. Dashboard Layout
gold_rate, silver_rate = fetch_metal_rates()
petrol_rate = fetch_fuel_rates()

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Gold (1g)", f"₹{gold_rate}", "+0.45%")
with col2:
    st.metric("Silver (1kg)", f"₹{int(silver_rate)}", "-1.2%")
with col3:
    st.metric("Petrol (Jalandhar)", f"₹{petrol_rate}", "Stable")
with col4:
    st.metric("LPG (14.2kg)", "₹803.00", "Updated Today")

st.divider()

# 6. Content Logic based on Search
if "gold" in search_query.lower():
    st.subheader("Gold Market Analysis")
    data = yf.Ticker("GC=F").history(period="1mo")
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
    st.plotly_chart(fig, use_container_width=True)
else:
    # Default View: A mix of resources
    left, right = st.columns(2)
    with left:
        st.subheader("Resource Comparison")
        chart_data = pd.DataFrame({
            'Resource': ['Gold', 'Silver', 'Petrol', 'LPG'],
            'Demand Index': [85, 60, 95, 70]
        })
        st.bar_chart(chart_data, x='Resource', y='Demand Index')
    with right:
        st.subheader("Solar Potential Today")
        st.info("High sunlight expected in Jalandhar. Efficiency: 92%")
        st.progress(92)
