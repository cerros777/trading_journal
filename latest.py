import streamlit as st
import pandas as pd


def render_latest_trades(df):
    recent_trades = df.sort_values("Date", ascending=False).head(5)
    for _, row in recent_trades.iterrows():
        st.markdown(f"""
        <div style='border:1px solid #444; border-radius:10px; padding:10px; margin-bottom:6px; background-color:#1e1e1e;'>
            <b>{row['Date'].strftime('%Y-%m-%d %H:%M')}</b> |
            <span style='color:#0af;'>{row['Name']}</span> |
            <b>{row['Action']}</b> |
            <b style='color:{'limegreen' if row['Total Position PnL'] > 0 else 'tomato'}'>{row['Total Position PnL']:.2f}</b><br>
            <i>{row['Notes'] if pd.notna(row['Notes']) else '—'}</i>
        </div>
        """, unsafe_allow_html=True)