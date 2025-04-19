def calculate_overall_stats(df):
    total_trades = len(df)
    win_trades = df[df["Total Position PnL"] > 0]
    loss_trades = df[df["Total Position PnL"] < 0]

    stats = {
        "total": total_trades,
        "wins": len(win_trades),
        "losses": len(loss_trades),
        "profit": df["Total Position PnL"].sum(),
        "max_win": df["Total Position PnL"].max(),
        "max_loss": df["Total Position PnL"].min(),
        "win_rate": len(win_trades) / total_trades * 100 if total_trades > 0 else 0,
        "avg_win": win_trades["Total Position PnL"].mean() if not win_trades.empty else 0,
        "avg_loss": loss_trades["Total Position PnL"].mean() if not loss_trades.empty else 0,
    }

    stats["expectancy"] = (stats["win_rate"]/100 * stats["avg_win"]) + ((1 - stats["win_rate"]/100) * stats["avg_loss"])
    stats["pnl_pct"] = (stats["profit"] / 100 * 100) if 100 != 0 else 0  # assumes base value 100
    return stats


def calculate_filtered_stats(df, all_df):
    if df.empty:
        return None

    stats = calculate_overall_stats(df)
    stats["previous_pnl"] = all_df[all_df["Date"] < df["Date"].min()]["Total Position PnL"].sum() + 100
    stats["pnl_pct"] = (stats["profit"] / stats["previous_pnl"]) * 100 if stats["previous_pnl"] != 0 else 0
    return stats
