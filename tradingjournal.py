import pandas as pd
from datetime import datetime
import shutil
import os

def update_trading_journal(latest_file, master_file):
    # Load the latest trades (user-uploaded file)
    latest_trades = pd.read_excel(latest_file)
    
    # Clean currency columns
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
    
    # Parse dates from latest trades.
    # Example input: "04.03.2023 10:30 AM UTC"
    latest_trades["Date"] = pd.to_datetime(
        latest_trades["Date"],
        format="%d.%m.%Y %I:%M %p %Z",  # includes the "UTC" part
        errors='coerce',
        dayfirst=True
    ).dt.tz_localize(None).dt.normalize()
    
    # Load or create the master journal.
    try:
        master_journal = pd.read_excel(master_file)
        # Backup the existing master journal.
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
    
    # Normalize dates in the master journal as well.
    master_journal["Date"] = pd.to_datetime(master_journal["Date"], errors='coerce')\
                              .dt.tz_localize(None).dt.normalize()
    
    # Ensure required columns exist in both DataFrames.
    required_columns = ["Date", "Name", "Action", "Quantity", "Price", "Value", "Total Position PnL", "Ratio", "Notes"]
    for col in required_columns:
        if col not in master_journal.columns:
            master_journal[col] = None
        if col not in latest_trades.columns:
            latest_trades[col] = None

    # Convert Notes and Ratio to strings.
    master_journal["Notes"] = master_journal["Notes"].astype(str)
    latest_trades["Notes"] = latest_trades["Notes"].astype(str)
    master_journal["Ratio"] = master_journal["Ratio"].astype(str)
    latest_trades["Ratio"] = latest_trades["Ratio"].astype(str)
    
    # Merge using a key based on Date, Name, Action, Quantity, and Price.
    trade_key = ["Date", "Name", "Action", "Quantity", "Price"]
    merged = pd.merge(
        latest_trades,
        master_journal,
        on=trade_key,
        how="left",
        suffixes=('', '_old')
    )
    
    # Preserve old Notes and Ratio if present.
    merged["Notes"] = merged["Notes"].combine_first(merged["Notes_old"])
    merged["Ratio"] = merged["Ratio"].combine_first(merged["Ratio_old"])
    merged = merged[required_columns]
    
    # Merge back with the master journal and deduplicate.
    combined = pd.concat([master_journal, merged], ignore_index=True)
    combined = combined.drop_duplicates(subset=trade_key, keep="last")
    
    # Format the Date column as a uniform string.
    # For example: "04-03-23 00:00"
    combined["Date"] = pd.to_datetime(combined["Date"], errors='coerce')\
                         .dt.strftime("%d-%m-%y 00:00")
    
    # Save the updated master journal.
    combined.to_excel(master_file, index=False)
    print(f"✅ Trading journal updated and saved as {master_file}")
