"""
Script: 01_ingest_strike_data.py
Description: Downloads the FAA Wildlife Strike ZIP file, extracts Excel, 
             and performs a full load into Aiven MySQL.
Author: Levi Altringer
Date: 2026-01-27
"""

# IMPORTS
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
import requests
import zipfile
import io

# LOAD .env FILE
load_dotenv()

# DATABASE CREDENTIALS (Aiven)
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# DIRECT URL DOWNLOAD
DATA_URL = "https://wildlife.faa.gov/assets/database_excel.zip"

# DATA DOWNLOAD AND INGESTION FUNCTION
def run_full_ingestion():
    try:
        # --- PHASE 1: DOWNLOAD ---
        print("Downloading ZIP...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(DATA_URL, headers=headers)
        response.raise_for_status()

        # --- PHASE 2: EXTRACT DATA FROM EXCEL FILE ---
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            excel_files = [f for f in z.namelist() if f.endswith('.xlsx')]
            target_file = excel_files[0]
            print(f"Reading {target_file}...")
            with z.open(target_file) as f:
                df = pd.read_excel(f, engine='calamine')

        # --- PHASE 3: TRANSFORM ---
        print(f"Loaded {len(df)} rows. Cleaning headers...")
        df.columns = [c.replace(' ', '_').replace('/', '_').replace('-', '_').lower() for c in df.columns]

        # --- PHASE 4: FAST UPLOAD ---
        print("Pushing to Aiven MySQL (using multi-row inserts)...")
        uri = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
        engine = create_engine(uri, connect_args={"ssl": {"ssl_mode": "REQUIRED"}})

        try:
            with engine.connect() as conn:
                print("Successfully connected to Aiven with SSL!")
        except Exception as e:
            print(f"Connection failed: {e}")
            return 

        df.to_sql(
            'wildlife_strikes_raw', 
            engine, 
            if_exists='replace', 
            index=False, 
            chunksize=1000, 
            method='multi' 
        )
        
        print("SUCCESS!")

    except Exception as e:
        print(f"Pipeline failed: {e}")

# EXECUTE DATA DOWNLOAD AND INGESTION
if __name__ == "__main__":
    run_full_ingestion()