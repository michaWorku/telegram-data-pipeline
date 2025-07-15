import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")

def get_db_connection():
    """
    Establishes and returns a PostgreSQL database connection.
    This function is designed to be called for each request or as needed
    to ensure fresh connections.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Database connection failed: {e}")
        # In a real application, you might want to log this and raise an HTTPException
        raise

def get_db():
    """
    Dependency to provide a database connection for FastAPI endpoints.
    Ensures the connection is closed after the request.
    """
    conn = None
    try:
        conn = get_db_connection()
        yield conn
    finally:
        if conn:
            conn.close()

