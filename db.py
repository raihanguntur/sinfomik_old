import mysql.connector
import streamlit as st
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="C:/Users/Han/sinfomik/db.env")

@st.cache_resource
def get_db_config():
    return {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME"),
        "port": 3306
    }

@contextmanager
def get_connection():
    config = get_db_config()
    conn = mysql.connector.connect(**config)
    try:
        yield conn
    finally:
        conn.close()
