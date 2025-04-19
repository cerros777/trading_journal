import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from datetime import timedelta
import math
from datetime import datetime
from tradingjournal import update_trading_journal
from filters import apply_date_filter
from metrics import calculate_overall_stats, calculate_filtered_stats
from visuals import plot_equity, plot_drawdown
from components import generate_stats_html
from latest import render_latest_trades
from history import render_trade_history


st.set_page_config(page_title="Trading Journal Dashboard.", layout="wide")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
st.markdown(open("header_nav.html").read(), unsafe_allow_html=True)

# --- Content Wrapper ---
st.markdown('<div class="content">', unsafe_allow_html=True)

# --- Upload Section ---
st.sidebar.header("📤 Upload New Trades")
uploaded_file = st.sidebar.file_uploader("Upload latest_trades.xlsx", type=["xlsx"])

if "prev_uploaded_file" not in st.session_state:
    st.session_state.prev_uploaded_file = None

if uploaded_file is not None:
    # Check if the uploaded file is different from the last uploaded file.
    if uploaded_file != st.session_state.prev_uploaded_file:
        st.session_state.prev_uploaded_file = uploaded_file  # Update stored file
        temp_file_path = "uploaded_latest_trades.xlsx"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        update_trading_journal(temp_file_path, "trading_journal.xlsx")
        st.cache_data.clear()
        st.rerun()  # 
        st.stop()
# --- Load Data ---
@st.cache_data
def load_data(file):
    df = pd.read_excel(file, parse_dates=["Date"])
    # Use the same date format as saved in tradingjournal.py
    df = df.dropna(subset=["Date"])
    df = df[df["Total Position PnL"].notna()]


    return df

df = load_data("trading_journal.xlsx")
print(f"loaded data {df}")

st.title("📘 Trading Journal")
col1, col2 = st.columns(2)
with col1:
    filter_opt = st.selectbox("Select Date Range", ["Last Day", "Last 7 Days", "Last 30 Days", "All Time"], key="stats_filter")
    filtered_df = apply_date_filter(df, filter_opt)
    stats = calculate_filtered_stats(filtered_df, df)
    st.subheader(f"Stats for {filter_opt}")
    st.markdown(generate_stats_html(stats), unsafe_allow_html=True)

with col2:
    st.subheader("Stats Summary")
    overall_stats = calculate_overall_stats(df)
    st.markdown(generate_stats_html(overall_stats), unsafe_allow_html=True)

# --- Charts ---
col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    chart_filter = st.selectbox("Equity Date Range", ["Last 7 Days", "Last 30 Days", "All Time"], key="equity_filter")
    eq_df = apply_date_filter(df, chart_filter)
    st.subheader("\U0001F4C8 Equity Curve")
    st.plotly_chart(plot_equity(eq_df), use_container_width=True)

with col_chart2:
    st.subheader("\U0001F4C9 Drawdown Curve")
    st.plotly_chart(plot_drawdown(eq_df), use_container_width=True)

# --- Latest 5 Trades Section ---
st.subheader("🧾 Latest 5 Trades")
render_latest_trades(df)

# --- Full History Table Section ---
st.subheader("📜 Full History")
render_trade_history(df)

st.markdown('</div>', unsafe_allow_html=True)