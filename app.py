import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import math
from datetime import datetime
from tradingjournal import update_trading_journal

st.set_page_config(page_title="Trading Journal Dashboard", layout="wide")

st.markdown("""
    <style>
    /* Small Nav Bar */
    .small-nav {
        text-align: right;
        font-size: 14px;
        margin-top: 60px;

    }
    .small-nav a {
        margin-left: 15px;
        color: #white;
        text-decoration: none;
    }
    .small-nav a:hover {
        text-decoration: underline;
    }
    /* List Cards */
    ul.metrics-list {
        list-style: none;
        padding: 0;
        margin: 10;
        line-height: 1.6;
        font-size: 0.95rem;
        column-count: 2;
        column-gap: 0.5rem
    }
    ul.metrics-list li {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0px;
        margin-bottom: 1rem;
        margin-right: 0.5rem;
    }
    ul.metrics-list li .stat-title {
          flex: 1;
          text-align: left;
          
      }
      ul.metrics-list li .stat-value {
          flex: 1;
          text-align: right;
          font-weight: bold;
      }
    /*Cards */
    [data-testid="stColumn"] {
        background-color: rgb(38, 39, 48);
        border:1px solid #30363D;
        border-radius: 10px;
        padding: 10px; 
    }
    /* Table Styling */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        font-size: 0.85rem;
        background-color: #1e1e1e;
    }
    .custom-table th, .custom-table td {
        padding: 10px 15px;
        border: 1px solid #333;
    }
    .custom-table th {
        background-color: #222;
        color: #f0f0f0;
        text-align: left;
    }
    .custom-table tr:nth-child(even) {
        background-color: #2a2a2a;
    }
    .custom-table tr:hover {
        background-color: #333;
    }
    .custom-table td.notes {
        width: 40%;
        color: #aaa;
        font-style: italic;
    }
    .custom-table td:not(.notes) {
        color: #ddd;
        text-align: center;
    }
            /* Fixed header container */
    .fixed-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 100;
        padding: 10px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .fixed-header .title {
        color: #fff;
        font-size: 24px;
        font-weight: bold;
    }
    .fixed-header .small-nav a {
        margin-left: 15px;
        color: white;
        text-decoration: none;
        font-size: 14px;
    }
    .fixed-header .small-nav a:hover {
        text-decoration: underline;
    }
    /* Add top margin to content so it doesn't get hidden behind the fixed header */
    .content {
        margin-top: 70px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Fixed Header with Nav Bar ---
st.markdown("""
<div class="fixed-header">
    <div class="title"></div>
    <div class="small-nav">
        <a href="#11c4484c">Summary</a>
        <a href="#1576484b">Equity</a>
        <a href="#1576484b">Drawdown</a>
        <a href="#f886712d">5 Trades</a>
        <a href="#90f118c4">History</a>
    </div>
</div>
""", unsafe_allow_html=True)

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

# --- Overall Metrics Calculations ---
total_trades = len(df)
win_trades = df[df["Total Position PnL"] > 0]
loss_trades = df[df["Total Position PnL"] < 0]
total_wins = len(win_trades)
total_losses = len(loss_trades)
total_profit = df["Total Position PnL"].sum()
total_value = 100
total_return_pct = (total_profit / total_value * 100) if total_value != 0 else 0
win_rate = total_wins / total_trades * 100 if total_trades > 0 else 0
avg_win = win_trades["Total Position PnL"].mean() if not win_trades.empty else 0
avg_loss = loss_trades["Total Position PnL"].mean() if not loss_trades.empty else 0
max_win = df["Total Position PnL"].max()
max_loss = df["Total Position PnL"].min()
expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)

# --- Last Day Metrics ---
df["Date"] = pd.to_datetime(df["Date"], errors="coerce") 
last_date = df["Date"].max().date()
last_day_df = df[df["Date"].dt.date == last_date]
last_day_trades = df[(df["Date"].dt.date == last_date) & df["Total Position PnL"].notna()]


if not last_day_trades.empty:
    total_last = len(last_day_trades)
    wins_last = (last_day_trades["Total Position PnL"] > 0).sum()
    losses_last = (last_day_trades["Total Position PnL"] < 0).sum()
    pnl_last = last_day_trades["Total Position PnL"].sum()
    #pnl_last_pct = pnl_last / total_last * 100
    win_rate_last = wins_last / total_last * 100 if total_last > 0 else 0
    avg_win_last = 0.0 if math.isnan(last_day_trades[last_day_trades["Total Position PnL"] > 0]["Total Position PnL"].mean()) else last_day_trades[last_day_trades["Total Position PnL"] > 0]["Total Position PnL"].mean()
    avg_loss_last = 0.0 if math.isnan(last_day_trades[last_day_trades["Total Position PnL"] < 0]["Total Position PnL"].mean()) else last_day_trades[last_day_trades["Total Position PnL"] < 0]["Total Position PnL"].mean()
    expectancy_last = ((0.0 if math.isnan(win_rate_last) else win_rate_last) / 100 * (0.0 if math.isnan(avg_win_last) else avg_win_last)) + ((1 - (0.0 if math.isnan(win_rate_last) else win_rate_last) / 100) * (0.0 if math.isnan(avg_loss_last) else avg_loss_last))
    previous_cumulative_pnl = df[df["Date"].dt.date < last_date]["Total Position PnL"].sum()+100
    if previous_cumulative_pnl != 0:
        pnl_last_pct = (pnl_last / previous_cumulative_pnl) * 100
    else:
        pnl_last_pct = None  # Or handle the zero case as needed

    
    latest_trading_day_stats = f"""
    <ul class="metrics-list">
    <li>
        <span class="stat-title">💼 Trades</span>
        <span class="stat-value">{total_last}</span>
    </li>
    <li>
        <span class="stat-title">✅ Wins</span>
        <span class="stat-value">{wins_last}</span>
    </li>
    <li>
        <span class="stat-title">❌ Losses</span>
        <span class="stat-value">{losses_last}</span>
    </li>
    <li>
        <span class="stat-title">📈 Max Win</span>
        <span class="stat-value">${last_day_trades['Total Position PnL'].max():.2f}</span>
    </li>
    <li>
        <span class="stat-title">📉 Max Loss</span>
        <span class="stat-value">${(last_day_trades[last_day_trades['Total Position PnL'] < 0]['Total Position PnL'].min() if not last_day_trades[last_day_trades['Total Position PnL'] < 0].empty else 0.0):.2f}</span>
    </li>
    <li>
        <span class="stat-title">🏆 Win Rate</span>
        <span class="stat-value">{win_rate_last:.1f}%</span>
    </li>
    <li>
        <span class="stat-title">📊 Avg Win</span>
        <span class="stat-value">${avg_win_last:.2f}</span>
    </li>
    <li>
        <span class="stat-title">📊 Avg Loss</span>
        <span class="stat-value">${avg_loss_last:.2f}</span>
    </li>
    <li>
        <span class="stat-title">💡 Expectancy</span>
        <span class="stat-value">{expectancy_last:.2f}</span>
    </li>
    <li>
        <span class="stat-title">💰 Total PnL</span>
        <span class="stat-value">
        <span class="stat-value">${pnl_last:.2f}</span>
        </span>
    </li>
    <li>
        <span class="stat-title">💰 Total Return(%)</span>
        <span class="stat-value">
        <span style="color:{'limegreen' if pnl_last_pct > 0 else 'tomato'};">{pnl_last_pct:.2f}%</span>
        </span>
    </li>
    </ul>
    """

else:
    latest_trading_day_stats = "<p>No valid trades found for the last trading day.</p>"

# --- Stats Summary (Overall) ---
stats_summary = f"""
<ul class="metrics-list">
    <li>
        <span class="stat-title">💼 Total Trades</span>
        <span class="stat-value">{total_trades}</span>
    </li>
    <li>
        <span class="stat-title">✅ Wins</span>
        <span class="stat-value">{total_wins}</span>
    </li>
    <li>
        <span class="stat-title">❌ Losses</span>
        <span class="stat-value">{total_losses}</span>
    </li>
    <li>
        <span class="stat-title">📈 Max Win</span>
        <span class="stat-value">{max_win:.2f}</span>
    </li>
    <li>
        <span class="stat-title">📉 Max Loss</span>
        <span class="stat-value">{max_loss:.2f}</span>
    </li>
    <li>
        <span class="stat-title">🏆 Win Rate</span>
        <span class="stat-value">{win_rate:.1f}%</span>
    </li>
    <li>
        <span class="stat-title">📊 Avg Win</span>
        <span class="stat-value">{avg_win:.2f}</span>
    </li>
    <li>
        <span class="stat-title">📊 Avg Loss</span>
        <span class="stat-value">{avg_loss:.2f}</span>
    </li>
    <li>
        <span class="stat-title">💡 Expectancy</span>
        <span class="stat-value">{expectancy:.2f}</span>
    </li>
    <li>
        <span class="stat-title">💰 Total PnL</span>
        <span class="stat-value">{total_profit:.2f}</span>
    </li>
    <li>
        <span class="stat-title">📊 Total Return (%)</span>
        <span class="stat-value"><span style="color:{'limegreen' if total_return_pct > 0 else 'tomato'};">{total_return_pct:.2f}%</span></span>
    </li>
</ul>
"""

# --- Equity Curve Calculation ---
df_equity = df.copy()
df_equity["Date"] = pd.to_datetime(df_equity["Date"]).dt.date
daily_pnl = df_equity.groupby("Date")["Total Position PnL"].sum().reset_index()
daily_pnl["Cumulative PnL"] = daily_pnl["Total Position PnL"].cumsum()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=daily_pnl["Date"],
    y=daily_pnl["Cumulative PnL"],
    mode="lines+markers",
    line=dict(color="#00BFFF", width=3),
    marker=dict(size=5),
    hovertemplate="Date: %{x}<br>Cumulative PnL: %{y:.2f}<extra></extra>",
    name="Equity"
))
fig.update_layout(
    title="💼 Cumulative Profit Over Time",
    xaxis_title="Date",
    yaxis_title="Cumulative PnL",
    hovermode="x unified",
    template="plotly_dark",
    height=400
)

# --- Drawdown Calculation ---
daily_pnl["Running Peak"] = daily_pnl["Cumulative PnL"].cummax()
daily_pnl["Drawdown"] = daily_pnl["Cumulative PnL"] - daily_pnl["Running Peak"]

fig_dd = go.Figure()
fig_dd.add_trace(go.Scatter(
    x=daily_pnl["Date"],
    y=daily_pnl["Drawdown"],
    mode="lines",
    line=dict(color="crimson", width=3),
    hovertemplate="Date: %{x}<br>Drawdown: %{y:.2f}<extra></extra>",
))
fig_dd.update_layout(
    title="📉 Drawdown Over Time",
    xaxis_title="Date",
    yaxis_title="Drawdown",
    hovermode="x unified",
    template="plotly_dark",
    height=400
)

# --- Layout: Top Row with 3 Columns for Cards ---
st.title("📘 Trading Journal")
col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Last Day Stats {last_date}")
    st.markdown(latest_trading_day_stats, unsafe_allow_html=True)
with col2:
    st.subheader("Stats Summary")
    st.markdown(stats_summary, unsafe_allow_html=True)


# --- Layout: Second Row with 2 Columns for Charts ---
col_ec, col_dd = st.columns(2)
with col_ec:
    st.subheader("📈 Equity Curve")
    st.plotly_chart(fig, use_container_width=True)
with col_dd:
    st.subheader("📉 Drawdown Curve")
    st.plotly_chart(fig_dd, use_container_width=True)                                                                                               

# --- Latest 5 Trades Section ---
st.subheader("🧾 Latest 5 Trades")
recent_trades = df.sort_values("Date", ascending=False).head(5)
for i, row in recent_trades.iterrows():
    st.markdown(f"""
    <div style='border:1px solid #444; border-radius:10px; padding:10px; margin-bottom:6px; background-color:#1e1e1e;'>
        <b>{row['Date'].strftime('%Y-%m-%d %H:%M')}</b> |
        <span style='color:#0af;'>{row['Name']}</span> |
        <b>{row['Action']}</b> |
        <b style='color:{'limegreen' if row['Total Position PnL'] > 0 else 'tomato'}'>{row['Total Position PnL']:.2f}</b><br>
        <i>{row['Notes'] if pd.notna(row['Notes']) else '—'}</i>
    </div>
    """, unsafe_allow_html=True)

# --- Full History Table Section ---
st.subheader("📜 Full History")
completed_trades = df[df["Total Position PnL"].notna()].sort_values("Date", ascending=False).copy()

page_size = 10
total_pages = max(1, (len(completed_trades) - 1) // page_size + 1)
page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)

start = (page - 1) * page_size
end = start + page_size
paginated_trades = completed_trades.iloc[start:end]

table_html = """
<style>
.custom-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    font-size: 0.85rem;
    background-color: #1e1e1e;
}
.custom-table th, .custom-table td {
    padding: 10px 15px;
    border: 1px solid #333;
}
.custom-table th {
    background-color: #222;
    color: #f0f0f0;
    text-align: left;
}
.custom-table tr:nth-child(even) {
    background-color: #2a2a2a;
}
.custom-table tr:hover {
    background-color: #333;
}
.custom-table td.notes {
    width: 40%;
    color: #aaa;
    font-style: italic;
}
.custom-table td:not(.notes) {
    color: #ddd;
    text-align: center;
}
</style>
<table class="custom-table">
<thead>
<tr>
    <th>Date</th>
    <th>Name</th>
    <th>Action</th>
    <th>Quantity</th>
    <th>Price</th>
    <th>PnL</th>
    <th>Notes</th>
</tr>
</thead>
<tbody>
"""

for _, row in paginated_trades.iterrows():
    note = row["Notes"] if pd.notna(row["Notes"]) and str(row["Notes"]).strip().lower() != "nan" else "—"
    pnl_color = "limegreen" if row["Total Position PnL"] > 0 else "tomato"
    table_html += f"""
    <tr>
        <td>{row['Date'].strftime('%Y-%m-%d')}</td>
        <td>{row['Name']}</td>
        <td>{row['Action']}</td>
        <td>{row['Quantity']}</td>
        <td>{row['Price']}</td>
        <td style="color:{pnl_color}">{row['Total Position PnL']:.2f}</td>
        <td class="notes">{note}</td>
    </tr>
    """
table_html += "</tbody></table>"

st.components.v1.html(table_html, height=500, scrolling=True)
