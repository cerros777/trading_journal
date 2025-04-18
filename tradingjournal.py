import pandas as pd
from datetime import datetime
import shutil
import os
import numpy as np
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def download_from_supabase(local_path="trading_journal.xlsx", bucket="trading-journal", storage_path="trading_journal.xlsx"):
    try:
        res = supabase.storage.from_(bucket).download(storage_path)
        with open(local_path, "wb") as f:
            f.write(res)
        print("✅ Downloaded from Supabase")
    except Exception as e:
        print("⚠️ Could not download file from Supabase:", e)


def upload_to_supabase(local_file_path, bucket="trading-journal", storage_path="trading_journal.xlsx"):
    try:
        # Optional: Remove old version first
        try:
            supabase.storage.from_(bucket).remove([storage_path])
        except Exception as e:
            print("⚠️ Could not remove old file (probably doesn't exist):", e)

        # Upload new file
        with open(local_file_path, "rb") as f:
            supabase.storage.from_(bucket).upload(storage_path, f)
        print("✅ Uploaded to Supabase")
    except Exception as e:
        print("⚠️ Could not upload file to Supabase:", e)



def update_trading_journal(latest_file, master_file):
    # Load the latest trades (user-uploaded file)
    latest_trades = pd.read_excel(latest_file)

    latest_trades = latest_trades[
        latest_trades["Total Position PnL"].notna() & 
        (latest_trades["Total Position PnL"].astype(str).str.strip() != "")
    ]
    
    
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
        download_from_supabase(local_path=master_file)
        master_journal = pd.read_excel(master_file)

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

    master_journal["Notes"] = master_journal["Notes"].astype(str).replace({"nan": np.nan, "None": np.nan})
    latest_trades["Notes"] = latest_trades["Notes"].astype(str).replace({"nan": np.nan, "None": np.nan})
    master_journal["Ratio"] = master_journal["Ratio"].astype(str).replace({"nan": np.nan, "None": np.nan})
    latest_trades["Ratio"] = latest_trades["Ratio"].astype(str).replace({"nan": np.nan, "None": np.nan})
    
    # Drop duplicates from latest_trades based on trade key.
    trade_key = ["Date", "Name", "Action", "Quantity", "Price"]
    latest_trades = latest_trades.drop_duplicates(subset=trade_key, keep="last")
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
    combined["Date"] = pd.to_datetime(combined["Date"], errors='coerce')
    combined = combined.sort_values("Date")
    
    # Save the updated master journal.
    combined.to_excel(master_file, index=False)
    upload_to_supabase(master_file)
    print(f"✅ Trading journal updated and saved as {master_file}")
  # print(master_file)
