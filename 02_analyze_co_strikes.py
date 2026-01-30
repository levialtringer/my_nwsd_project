"""
Script: 02_analyze_co_strikes.py
Description: Pulls wildlife strikes data for Colorado airports.
Author: Levi Altringer
Date: 2026-01-27
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

load_dotenv()

# Setup connection
engine = create_engine(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

def check_colorado_stats():
    query = """
    SELECT state, airport, COUNT(*) as total_strikes
    FROM wildlife_strikes_raw
    WHERE state = 'CO'
    GROUP BY airport
    ORDER BY total_strikes DESC;
    """
    
    with engine.connect() as conn:
        df_co = pd.read_sql(text(query), conn)
        print("\n--- TOP COLORADO AIRPORTS FOR WILDLIFE STRIKES ---")
        print(df_co)

if __name__ == "__main__":
    check_colorado_stats()
