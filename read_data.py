import streamlit as st
from psycopg_pool import ConnectionPool
import psycopg
import pandas as pd

# --- Local .env file ---
# from dotenv import load_dotenv
# import os
# load_dotenv(override=True)
# conn_string = os.getenv("DATABASE_URL")


# --- Initialize database connection pool ---

# Define get_database_session() 
@st.cache_resource
def get_database_session(database_url):
    try: 
        # Create a database session object that points to the URL.
        pool = ConnectionPool(
            database_url, 
            min_size=1, 
            max_size=10
        ) # Initialize connection pool
        return pool
    except psycopg.OperationalError as e:
        st.error(f"Network is blocking connection to the database server.\nPlease try again on a different network/internet connection, or reach out to admin at ujcho@jacksongov.org.\n{e}")
        return None

# Establish NEON database connection (via psycopg3)
database_url = st.secrets["neonDB"]["database_url"]

# Attempt connection
try:
    db_connection = get_database_session(database_url)
except Exception as e:
    print(f"{e}")
    st.stop()


# --- Define function to read tables from Neon DB ---
@st.cache_data
def query_table(sql_query: str, _connection: ConnectionPool = db_connection) -> pd.DataFrame:
    if _connection is None:
        return pd.DataFrame()
    
    try:
        if isinstance(_connection, ConnectionPool):
            with _connection.connection() as conn:
                df = pd.read_sql(sql_query, conn)

        else:
            df = pd.read_sql(sql_query, _connection)

        return df
    
    except psycopg.OperationalError as e:
        st.error(f"Database query failed: {e}")
        return pd.DataFrame()

# Query tables 
RCVD = query_table("SELECT * FROM karpel_rcvd")
FLD = query_table("SELECT * FROM karpel_fld")
NTFLD = query_table("SELECT * FROM karpel_ntfld")
DISP = query_table("SELECT * FROM karpel_disp")