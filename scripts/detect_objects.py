import os
import json
import logging
from datetime import datetime
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from ultralytics import YOLO
from ultralytics.utils.downloads import download # Import the download utility

# --- Configuration and Environment Setup ---
load_dotenv()

# PostgreSQL connection details from environment variables
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

# Data Lake paths (where images are stored)
BASE_DATA_PATH = 'data/raw'
TELEGRAM_IMAGES_PATH = os.path.join(BASE_DATA_PATH, 'images')

# Define a directory within your project to store downloaded YOLO models
# This will be /app/yolo_models inside the Docker container
YOLO_MODELS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'yolo_models')
os.makedirs(YOLO_MODELS_PATH, exist_ok=True) # Ensure the directory exists

# Define the path where the YOLO model weights will be stored
# YOLO_MODEL_NAME = 'yolov8n.pt'
# YOLO_MODEL_NAME = 'yolov8s.pt'
YOLO_MODEL_NAME = 'yolov8m.pt'  # Use a medium model for better accuracy
YOLO_MODEL_FULL_PATH = os.path.join(YOLO_MODELS_PATH, YOLO_MODEL_NAME)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("object_detection.log"), # Log to a file
        logging.StreamHandler()                      # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# --- Database Connection and Schema Management ---

def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            dbname=POSTGRES_DB
        )
        logger.info("Successfully connected to PostgreSQL.")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise

def setup_raw_image_detections_table(conn):
    """
    Ensures the raw.image_detections table exists in the PostgreSQL database.
    This table will store raw YOLO detection results.
    """
    try:
        with conn.cursor() as cur:
            # Create raw schema if it doesn't exist
            cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS raw"))
            conn.commit()
            logger.info("Ensured 'raw' schema exists.")

            # Create image_detections table
            cur.execute(sql.SQL("""
                CREATE TABLE IF NOT EXISTS raw.image_detections (
                    id SERIAL PRIMARY KEY,
                    message_id BIGINT NOT NULL,
                    image_path TEXT NOT NULL,
                    detected_object_class TEXT NOT NULL,
                    confidence_score NUMERIC(5, 4) NOT NULL,
                    detection_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    -- Add a unique constraint to prevent duplicate detections for the same image/object
                    UNIQUE (message_id, image_path, detected_object_class)
                );
            """))
            conn.commit()
            logger.info("Ensured 'raw.image_detections' table exists.")
    except Exception as e:
        logger.error(f"Error setting up raw.image_detections table: {e}")
        raise

# --- Object Detection Logic ---

def load_yolo_model():
    """Loads a pre-trained YOLOv8 model, handling download explicitly."""
    try:
        # Check if model already exists locally
        if not os.path.exists(YOLO_MODEL_FULL_PATH):
            logger.info(f"Downloading YOLOv8n model weights to: {YOLO_MODEL_FULL_PATH}")
            # Use ultralytics' internal download utility
            download(f'https://github.com/ultralytics/assets/releases/download/v8.1.0/{YOLO_MODEL_NAME}', YOLO_MODELS_PATH)
            logger.info("YOLOv8n model weights downloaded successfully.")
        else:
            logger.info(f"YOLOv8n model weights already exist at: {YOLO_MODEL_FULL_PATH}")

        # Load the model from the local path
        model = YOLO(YOLO_MODEL_FULL_PATH)
        logger.info("YOLOv8n model loaded successfully.")
        return model
    except Exception as e:
        logger.critical(f"Failed to load YOLOv8 model: {e}", exc_info=True)
        raise

def get_processed_image_ids(conn):
    """
    Retrieves a set of message_ids for images that have already been processed
    and have entries in raw.image_detections.
    """
    processed_ids = set()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT message_id FROM raw.image_detections")
            for row in cur.fetchall():
                processed_ids.add(row[0])
        logger.info(f"Found {len(processed_ids)} previously processed image message IDs.")
    except Exception as e:
        logger.error(f"Error retrieving processed image IDs: {e}")
    return processed_ids

def process_image_for_detection(model, image_full_path, message_id, conn):
    """
    Performs object detection on a single image and stores results in the database.
    """
    try:
        logger.info(f"Processing image: {image_full_path} (Message ID: {message_id})")
        
        # Perform inference
        results = model(image_full_path) #, conf=0.1,  imgsz=640) # YOLOv8 returns a list of Results objects

        detections_found = 0
        with conn.cursor() as cur:
            for r in results:
                # Iterate over detected objects
                for box, cls, conf in zip(r.boxes.xyxy, r.boxes.cls, r.boxes.conf):
                    detected_class = model.names[int(cls)] # Get class name from model
                    confidence_score = float(conf)

                    # Insert into raw.image_detections
                    insert_query = sql.SQL("""
                        INSERT INTO raw.image_detections (
                            message_id, image_path, detected_object_class, confidence_score
                        ) VALUES (
                            %s, %s, %s, %s
                        ) ON CONFLICT (message_id, image_path, detected_object_class) DO NOTHING;
                    """)
                    cur.execute(insert_query, (
                        message_id,
                        image_full_path,
                        detected_class,
                        confidence_score
                    ))
                    detections_found += 1
            conn.commit()
        logger.info(f"Finished processing {image_full_path}. Found {detections_found} detections.")
        return True
    except Exception as e:
        logger.error(f"Error processing image {image_full_path}: {e}", exc_info=True)
        conn.rollback() # Rollback any partial transactions
        return False

# --- Main Execution Flow ---

def main():
    """Main function to scan images and perform object detection."""
    conn = None
    try:
        conn = get_db_connection()
        setup_raw_image_detections_table(conn)

        yolo_model = load_yolo_model()

        processed_image_ids = get_processed_image_ids(conn)

        # Walk through the images directory
        logger.info(f"Scanning for images in: {TELEGRAM_IMAGES_PATH}")
        if not os.path.exists(TELEGRAM_IMAGES_PATH):
            logger.error(f"Image directory does not exist: {TELEGRAM_IMAGES_PATH}")
            logger.error("Please ensure you have run the scraping script and images are in data/raw/images on your host.")
            return

        images_found = False
        for root, _, files in os.walk(TELEGRAM_IMAGES_PATH):
            for file in files:
                # Filter for common image extensions
                if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    logger.debug(f"Skipping non-image file: {file}")
                    continue

                images_found = True
                # Assuming image filenames are message_id.ext
                try:
                    message_id = int(os.path.splitext(file)[0])
                except ValueError:
                    logger.warning(f"Skipping non-numeric filename (expected message_id): {file}")
                    continue

                if message_id in processed_image_ids:
                    logger.debug(f"Image {message_id} already processed. Skipping.")
                    continue

                image_full_path = os.path.join(root, file)
                if not os.path.isfile(image_full_path):
                    logger.warning(f"File not found or not a file (after path join): {image_full_path}")
                    continue

                # Process the image and add its message_id to the processed set if successful
                if process_image_for_detection(yolo_model, image_full_path, message_id, conn):
                    processed_image_ids.add(message_id) # Add to set to avoid re-processing in current run
        
        if not images_found:
            logger.warning(f"No image files found in {TELEGRAM_IMAGES_PATH}. Please ensure images are scraped and present.")

    except Exception as e:
        logger.critical(f"An error occurred during object detection process: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
            logger.info("PostgreSQL connection closed.")

if __name__ == '__main__':
    main()
