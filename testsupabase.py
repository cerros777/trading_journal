from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def download_from_supabase(local_path="trading_journal.xlsx", bucket="trading-journal", storage_path="trading_journal.xlsx"):
    try:
        res = supabase.storage.from_(bucket).download(storage_path)
        if res is None or res == b'':
            print("⚠️ Empty or invalid file from Supabase")
            return

        with open(local_path, "wb") as f:
            f.write(res)
        print("✅ Downloaded from Supabase")
    except Exception as e:
        print("⚠️ Could not download file from Supabase:", e)

# Test the download function
download_from_supabase()
