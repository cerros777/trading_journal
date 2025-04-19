import streamlit as st
import pandas as pd

def render_trade_history(df):
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