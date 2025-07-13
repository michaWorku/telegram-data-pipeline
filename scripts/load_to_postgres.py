import os
import json
import logging
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from datetime import datetime

# --- Configuration and Environment Setup ---
# Load environment variables from .env file
load_dotenv()

# PostgreSQL Database Credentials from environment variables
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')

# Data Lake path where raw messages are stored
RAW_MESSAGES_PATH = 'data/raw/telegram_messages'

# Target schema and table in PostgreSQL
TARGET_SCHEMA = 'raw'
TARGET_TABLE = 'telegram_messages'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("load_to_postgres.log"), # Log to a file
        logging.StreamHandler()                      # Also log to console
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("Successfully connected to PostgreSQL database.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}", exc_info=True)
        raise

def create_raw_table_if_not_exists(cursor):
    """
    Creates the raw schema and the telegram_messages table if they don't exist.
    The table will store raw JSON data in a jsonb column.
    """
    try:
        # Create schema if not exists
        cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(sql.Identifier(TARGET_SCHEMA)))
        logger.info(f"Schema '{TARGET_SCHEMA}' ensured.")

        # Create table if not exists
        # We use 'id' as primary key to prevent duplicate message inserts
        create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.{} (
                id BIGINT PRIMARY KEY,
                channel_id BIGINT,
                message_date TIMESTAMP WITH TIME ZONE,
                raw_data JSONB,
                load_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """).format(sql.Identifier(TARGET_SCHEMA), sql.Identifier(TARGET_TABLE))
        cursor.execute(create_table_query)
        logger.info(f"Table '{TARGET_SCHEMA}.{TARGET_TABLE}' ensured.")
    except Exception as e:
        logger.error(f"Error creating schema or table: {e}", exc_info=True)
        raise

def load_json_to_postgres():
    """
    Reads JSON files from the data lake and loads them into the PostgreSQL table.
    Handles incremental loading by checking if a message ID already exists.
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False # Use transactions for atomicity
        cursor = conn.cursor()

        create_raw_table_if_not_exists(cursor)

        total_files_processed = 0
        total_messages_loaded = 0
        total_duplicates_skipped = 0

        # Iterate through partitioned directories (YYYY-MM-DD/channel_name)
        for date_dir in os.listdir(RAW_MESSAGES_PATH):
            date_path = os.path.join(RAW_MESSAGES_PATH, date_dir)
            if not os.path.isdir(date_path):
                continue # Skip non-directory files

            for channel_dir in os.listdir(date_path):
                channel_path = os.path.join(date_path, channel_dir)
                if not os.path.isdir(channel_path):
                    continue # Skip non-directory files

                logger.info(f"Processing directory: {channel_path}")
                for filename in os.listdir(channel_path):
                    if filename.endswith('.json'):
                        file_path = os.path.join(channel_path, filename)
                        total_files_processed += 1
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                message_data = json.load(f)

                            message_id = message_data.get('id')
                            channel_id = message_data.get('channel_id')
                            message_date_str = message_data.get('date')
                            raw_message_json = json.dumps(message_data) # Store the entire loaded JSON

                            if message_id is None or channel_id is None or message_date_str is None:
                                logger.warning(f"Skipping file {filename} due to missing required fields (id, channel_id, or date).")
                                continue

                            # Convert date string to datetime object for PostgreSQL TIMESTAMP WITH TIME ZONE
                            message_date = datetime.fromisoformat(message_date_str)

                            # Check if message_id already exists to prevent duplicates
                            check_query = sql.SQL("SELECT id FROM {}.{} WHERE id = %s;").format(
                                sql.Identifier(TARGET_SCHEMA), sql.Identifier(TARGET_TABLE)
                            )
                            cursor.execute(check_query, (message_id,))
                            existing_id = cursor.fetchone()

                            if existing_id:
                                logger.debug(f"Message ID {message_id} already exists in DB. Skipping: {file_path}")
                                total_duplicates_skipped += 1
                            else:
                                insert_query = sql.SQL("""
                                    INSERT INTO {}.{} (id, channel_id, message_date, raw_data)
                                    VALUES (%s, %s, %s, %s);
                                """).format(sql.Identifier(TARGET_SCHEMA), sql.Identifier(TARGET_TABLE))
                                cursor.execute(insert_query, (message_id, channel_id, message_date, raw_message_json))
                                total_messages_loaded += 1
                                logger.debug(f"Loaded message {message_id} from {file_path}")

                        except json.JSONDecodeError as e:
                            logger.error(f"Error decoding JSON from {file_path}: {e}")
                        except Exception as e:
                            logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
                conn.commit() # Commit after processing each channel's directory
                logger.info(f"Committed changes for channel directory: {channel_path}")

        logger.info(f"Data loading complete. Total files processed: {total_files_processed}")
        logger.info(f"Total new messages loaded: {total_messages_loaded}")
        logger.info(f"Total duplicate messages skipped: {total_duplicates_skipped}")

    except Exception as e:
        logger.critical(f"An error occurred during data loading: {e}", exc_info=True)
        if conn:
            conn.rollback() # Rollback in case of error
            logger.info("Transaction rolled back due to error.")
    finally:
        if conn:
            conn.close()
            logger.info("PostgreSQL connection closed.")

if __name__ == '__main__':
    load_json_to_postgres()
