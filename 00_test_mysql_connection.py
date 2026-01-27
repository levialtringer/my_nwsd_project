"""
Script: 00_test_mysql_connection.py
Description: Simple handshake to verify Aiven MySQL connection and SSL.
Author: Levi Altringer
Date: 2026-01-27
"""

# IMPORTS
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# LOAD .env FILE
load_dotenv()

def test_connection():
    
    # GET CREDENTIALS
    USER = os.getenv("DB_USER")
    PASSWORD = os.getenv("DB_PASSWORD")
    HOST = os.getenv("DB_HOST")
    PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    # BUILD URI
    connection_uri = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

    try:
        # INITIALIZE ENGINE
        engine = create_engine(
            connection_uri,
            connect_args={"ssl": {"ssl_mode": "REQUIRED"}}
        )

        # EXECUTE CONNECTION CHECK
        with engine.connect() as conn:
            # SELECT 1 is the universal "Are you there?" query
            conn.execute(text("SELECT 1"))
            print("CONNECTION SUCCESSFUL: The server is responding.")

    except Exception as e:
        print("CONNECTION FAILED")
        print(f"Error details: {e}")
        
if __name__ == "__main__":
    test_connection()