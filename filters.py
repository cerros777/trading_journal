from datetime import timedelta
import pandas as pd

def apply_date_filter(df, period):
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    today = df["Date"].max().normalize()

    if period == "Last Day":
        return df[df["Date"].dt.date == today.date()]
    elif period == "Last week":
        return df[df["Date"] >= today - timedelta(days=6)]
    elif period == "Last month":
        return df[df["Date"] >= today - timedelta(days=29)]
    else:
        return df
