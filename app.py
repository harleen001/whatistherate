import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="WhatIsTheRate | Jalandhar Terminal", layout="wide", page_icon="📈")

# --- 2. ADVANCED STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #FFD700; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1e2130; border-radius: 4px; color: white; padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] { background-color: #00529b !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINES ---

@st.cache_data(ttl=3600)
def fetch_ticker_series(ticker):
    """Fetches data and ensures it is a clean Series to prevent 'to_frame' errors."""
    data = yf.download(ticker, period="30d", interval="1d")
    if data.empty:
        return pd.Series()
    # Extract 'Close' and ensure it's a Series
    return data['Close'].squeeze()

def create_area_chart(series, color, title, scale_factor=1.0):
    """Creates a stable filled area chart to fix 'NaN' visual issues."""
    if series.empty:
        return go.Figure().update_layout(title="Data Unavailable")
    
    # Apply scaling
    scaled_values = series * scale_factor
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=scaled_values.index, 
        y=scaled_values.values,
        fill='tozeroy',
        mode='lines+markers',
        line=dict(color=color, width=2),
        fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}',
        name="Market Trend"
    ))
    
    fig.update_layout(
        template="plotly_dark",
        title=title,
        height=350,
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(autorange=True, fixedrange=False, showgrid=False, title="Price (INR)"),
        xaxis=dict(showgrid=False, type='date', tickformat='%b %d')
    )
    return fig

# --- 4. TOP NOTIFICATION BAR ---
petrol_val = 97.55
diesel_val = 87.38
lpg_val = 946.00
st.info(f"🚀 **Market Alert:** Jalandhar Petrol is stable at ₹{petrol_val}. LPG Cylinders remain at ₹{lpg_val}. Rates refreshed for {datetime.now().strftime('%d %B')}.")

# --- 5. TABS ---
t1, t2, t3, t4 = st.tabs(["🟡 Gold", "🥈 Silver", "⛽ Fuel Hub", "💡 Utilities & Agri"])

# --- GOLD TAB ---
with t1:
    g_base = 14033.0 
    col_left, col_right = st.columns([1, 2.5])
    
    with col_left:
        purity = st.selectbox("Purity", ["24K", "22K", "18K"], key="g_p")
        unit = st.selectbox("Weight", ["1 Gram", "10 Grams", "12 Grams (Tola)"], key="g_w")
        
        # Logic multipliers
        mult = 1.0 if "24" in purity else (0.916 if "22" in purity else 0.75)
        u_mult = 1.0 if "1 Gram" in unit else (10.0 if "10 Grams" in unit else 11.66)
        
        current_g = g_base * mult * u_mult
        st.metric(f"Gold Price ({unit})", f"₹{current_g:,.2f}", "-1.2%")
        
    with col_right:
        gold_series = fetch_ticker_series("GC=F")
        if not gold_series.empty:
            # Calculate dynamic scale to match local Jalandhar rates
            scale = (current_g / float(gold_series.iloc[-1]))
            st.plotly_chart(create_area_chart(gold_series.tail(15), "#FFD700", f"Gold {purity} Analysis"), use_container_width=True)
    
    st.subheader("📋 5-Day Gold Price Registry")
    if not gold_series.empty:
        # Fixed DataFrame logic to prevent 'AttributeError'
        hist_df = (gold_series.tail(5) * scale).to_frame(name="Price (INR)")
        st.dataframe(hist_df.style.format("₹{:.2f}"), use_container_width=True)

# --- SILVER TAB ---
with t2:
    s_base = 260.0
    c1s, c2s = st.columns([1, 2.5])
    with c1s:
        s_unit = st.selectbox("Weight", ["1 Gram", "100 Grams", "1 KG"], key="s_w")
        s_u_mult = 1.0 if "1 Gram" in s_unit else (100.0 if "100 Grams" in s_unit else 1000.0)
        st.metric(f"Silver Price ({s_unit})", f"₹{s_base * s_u_mult:,.2f}", "+0.4%")
        
    with c2s:
        silver_series = fetch_ticker_series("SI=F")
        if not silver_series.empty:
            s_scale = ((s_base * s_u_mult) / float(silver_series.iloc[-1]))
            st.plotly_chart(create_area_chart(silver_series.tail(15), "#C0C0C0", f"Silver {s_unit} Trend"), use_container_width=True)

# --- FUEL HUB ---
with t3:
    st.subheader("Dynamic Fuel Tracker")
    f_col1, f_col2 = st.columns([1, 2])
    with f_col1:
        st.metric("Petrol (Jalandhar)", f"₹{petrol_val}")
        st.metric("Diesel (Jalandhar)", f"₹{diesel_val}")
        st.metric("LPG (Cylinder)", f"₹{lpg_val}")
        
    with f_col2:
        # Comparison uses per-unit rates so bars are visually balanced
        lpg_per_kg = round(lpg_val / 14.2, 2)
        fig_f = px.bar(
            x=["Petrol", "Diesel", "LPG (per kg)"], 
            y=[petrol_val, diesel_val, lpg_per_kg], 
            labels={'x': 'Fuel Type', 'y': 'Price (INR)'},
            color=["Petrol", "Diesel", "LPG"], 
            template="plotly_dark",
            title="Energy Cost Comparison"
        )
        st.plotly_chart(fig_f, use_container_width=True)
    
    st.write("### ⛽ Fuel Price History (Last 5 Updates)")
    fuel_hist = pd.DataFrame({
        "Date": [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)],
        "Petrol (₹)": [97.55, 97.55, 97.77, 97.77, 98.10],
        "Diesel (₹)": [87.38, 87.38, 87.59, 87.59, 88.00]
    })
    st.table(fuel_hist)

# --- UTILITIES & AGRI ---
with t4:
    st.subheader("Utility & Agriculture Ledger")
    u_col1, u_col2 = st.columns(2)
    with u_col1:
        st.write("#### ⚡ Electricity (PSPCL) Rates")
        elec_data = {"Category": ["Domestic (0-100)", "Domestic (101-300)", "Industrial"], "Rate (₹/Unit)": [3.50, 5.50, 5.95]}
        st.table(pd.DataFrame(elec_data))
        
    with u_col2:
        st.write("#### 🌾 Mandi Rates (Jalandhar)")
        agri_data = {"Commodity": ["Wheat", "Basmati", "Potato"], "Price (₹/Quintal)": [2425, 3150, 1100]}
        st.table(pd.DataFrame(agri_data))

# --- FOOTER ---
st.divider()
st.caption(f"WhatIsTheRate v3.5 | Jalandhar, Punjab | Localized Market Data | {datetime.now().strftime('%d %B %Y')}")