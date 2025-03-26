import pandas as pd
from datetime import datetime
import shutil
import os

def update_trading_journal(latest_file, master_file):
    # Load latest trades
    latest_trades = pd.read_excel(latest_file)

    # Clean currency values
    currency_columns = ["Price", "Value", "Total Position PnL"]
    for col in currency_columns:
        latest_trades[col] = (
            latest_trades[col]
            .astype(str)
            .str.replace(r"[₮$,]", "", regex=True)
            .str.replace(",", "")
            .str.strip()
            .replace("", "0")
            .astype(float)
        )

    # Normalize dates
    latest_trades["Date"] = pd.to_datetime(latest_trades["Date"], errors='coerce').dt.tz_localize(None).dt.normalize()

    # Load or create master journal
    try:
        master_journal = pd.read_excel(master_file)
        # Backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{os.path.splitext(master_file)[0]}_backup_{timestamp}.xlsx"
        shutil.copy(master_file, backup_path)
        print(f"🗂️ Backup saved to {backup_path}")
    except FileNotFoundError:
        print("Master journal not found. Creating a new one.")
        master_journal = pd.DataFrame(columns=[
            "Date", "Name", "Action", "Quantity", "Price", "Value",
            "Total Position PnL", "Ratio", "Notes"
        ])

    master_journal["Date"] = pd.to_datetime(master_journal["Date"], errors='coerce').dt.tz_localize(None).dt.normalize()

    # Ensure required columns exist and are correct dtype
    required_columns = ["Date", "Name", "Action", "Quantity", "Price", "Value", "Total Position PnL", "Ratio", "Notes"]
    for col in required_columns:
        if col not in master_journal.columns:
            master_journal[col] = None
        if col not in latest_trades.columns:
            latest_trades[col] = None

    master_journal["Notes"] = master_journal["Notes"].astype(str)
    latest_trades["Notes"] = latest_trades["Notes"].astype(str)
    master_journal["Ratio"] = master_journal["Ratio"].astype(str)
    latest_trades["Ratio"] = latest_trades["Ratio"].astype(str)

    # Merge on keys
    trade_key = ["Date", "Name", "Action", "Quantity", "Price"]
    merged = pd.merge(
        latest_trades,
        master_journal,
        on=trade_key,
        how="left",
        suffixes=('', '_old')
    )

    # Preserve Notes and Ratio from old
    merged["Notes"] = merged["Notes"].combine_first(merged["Notes_old"])
    merged["Ratio"] = merged["Ratio"].combine_first(merged["Ratio_old"])

    merged = merged[required_columns]

    # Merge back into master, deduplicate
    combined = pd.concat([master_journal, merged], ignore_index=True)
    combined = combined.drop_duplicates(subset=trade_key, keep="last")

    # Format final Date
    combined["Date"] = pd.to_datetime(combined["Date"], errors='coerce').dt.strftime("%d-%m-%y 00:00")

    # Save
    combined.to_excel(master_file, index=False)
    print(f"✅ Trading journal updated and saved as {master_file}")
