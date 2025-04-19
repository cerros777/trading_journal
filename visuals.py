import plotly.graph_objects as go

def plot_equity(df):
    df = df.copy()
    df["Date"] = df["Date"].dt.date
    daily = df.groupby("Date")["Total Position PnL"].sum().reset_index()
    daily["Cumulative PnL"] = daily["Total Position PnL"].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"],
        y=daily["Cumulative PnL"],
        mode="lines+markers",
        line=dict(color="#00BFFF", width=3),
        marker=dict(size=5),
        hovertemplate="Date: %{x}<br>Cumulative PnL: %{y:.2f}<extra></extra>"
    ))
    fig.update_layout(
        title="💼 Cumulative Profit Over Time",
        xaxis_title="Date",
        yaxis_title="Cumulative PnL",
        hovermode="x unified",
        template="plotly_dark",
        height=400
    )
    return fig


def plot_drawdown(df):
    df = df.copy()
    df["Date"] = df["Date"].dt.date
    daily = df.groupby("Date")["Total Position PnL"].sum().reset_index()
    daily["Cumulative PnL"] = daily["Total Position PnL"].cumsum()
    daily["Running Peak"] = daily["Cumulative PnL"].cummax()
    daily["Drawdown"] = daily["Cumulative PnL"] - daily["Running Peak"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"],
        y=daily["Drawdown"],
        mode="lines",
        line=dict(color="crimson", width=3),
        hovertemplate="Date: %{x}<br>Drawdown: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(
        title="📉 Drawdown Over Time",
        xaxis_title="Date",
        yaxis_title="Drawdown",
        hovermode="x unified",
        template="plotly_dark",
        height=400
    )
    return fig
