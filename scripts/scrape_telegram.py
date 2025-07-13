import os
import json
import logging
from datetime import datetime
import asyncio
import argparse
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
# Correct import for RPCError
from telethon.errors import RPCError # Corrected import
from dotenv import load_dotenv

# --- Configuration and Environment Setup ---
# Load environment variables from .env file
load_dotenv()

# Telegram API credentials from environment variables
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = 'telegram_scraper_session' # Session file to store auth info

# Data Lake paths
BASE_DATA_PATH = 'data/raw'
TELEGRAM_MESSAGES_PATH = os.path.join(BASE_DATA_PATH, 'telegram_messages')
TELEGRAM_IMAGES_PATH = os.path.join(BASE_DATA_PATH, 'images')

# Ensure data directories exist
os.makedirs(TELEGRAM_MESSAGES_PATH, exist_ok=True)
os.makedirs(TELEGRAM_IMAGES_PATH, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"), # Log to a file
        logging.StreamHandler()             # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# List of Telegram channels to scrape
# Add more channels from https://et.tgstat.com/medicine as needed
TELEGRAM_CHANNELS = [
    'https://t.me/CheMed123',
    'https://t.me/lobelia4cosmetics',
    'https://t.me/tikvahpharma',
    # Add more channels here
]

# --- Helper Functions ---

def get_latest_processed_message_id(channel_output_dir):
    """
    Checks the existing JSON files in the channel's output directory
    for the current day and returns the highest (newest) message ID found.
    This ID will be used as max_id to resume scraping older messages.
    """
    latest_id = None
    if os.path.exists(channel_output_dir):
        json_files = [f for f in os.listdir(channel_output_dir) if f.endswith('.json')]
        message_ids = []
        for f in json_files:
            try:
                # Extract message ID from filename (e.g., "12345.json" -> 12345)
                message_ids.append(int(f.split('.')[0]))
            except ValueError:
                logger.warning(f"Could not parse message ID from filename: {f} in {channel_output_dir}")
                continue
        if message_ids:
            latest_id = max(message_ids)
            logger.info(f"Found latest processed message ID in {channel_output_dir}: {latest_id}")
    return latest_id

async def download_media(message, channel_name, message_id):
    """
    Downloads media (photos/documents) from a Telegram message.
    Returns the local path to the downloaded file if successful, otherwise None.
    """
    if message.media:
        try:
            # Determine file extension based on media type
            if isinstance(message.media, MessageMediaPhoto):
                file_ext = '.jpg'
            elif isinstance(message.media, MessageMediaDocument):
                # Try to get extension from document attributes
                if message.media.document.mime_type:
                    mime_type = message.media.document.mime_type
                    if 'image' in mime_type:
                        file_ext = '.' + mime_type.split('/')[-1]
                    else:
                        # For other document types, we might want to skip or handle differently
                        logger.info(f"Skipping non-image document in message {message_id} from {channel_name}: {mime_type}")
                        return None
                else:
                    file_ext = '.bin' # Default binary if mime_type is missing
            else:
                logger.info(f"Unsupported media type in message {message_id} from {channel_name}: {type(message.media)}")
                return None

            # Define the path to save the image
            # Format: data/raw/images/channel_name/message_id.ext
            channel_image_path = os.path.join(TELEGRAM_IMAGES_PATH, channel_name.replace('@', ''))
            os.makedirs(channel_image_path, exist_ok=True)
            file_name = f"{message_id}{file_ext}"
            file_path = os.path.join(channel_image_path, file_name)

            logger.info(f"Downloading media for message {message_id} from {channel_name} to {file_path}")
            await message.download_media(file=file_path)
            logger.info(f"Successfully downloaded media for message {message_id}.")
            return file_path
        except Exception as e:
            logger.error(f"Error downloading media for message {message_id} from {channel_name}: {e}")
            return None
    return None

async def scrape_channel(client, channel_url, limit=None):
    """
    Scrapes messages and images from a given Telegram channel URL.
    Stores messages as JSON and images in the data lake.
    The 'limit' parameter controls the maximum number of messages to fetch.
    If a previous scrape was interrupted for the current day, it resumes from where it left off.
    """
    try:
        # Resolve channel entity
        entity = await client.get_entity(channel_url)
        channel_name = entity.username if entity.username else entity.title.replace(' ', '_')
        
        # Get today's date for partitioning
        today_str = datetime.now().strftime('%Y-%m-%d')
        channel_output_dir = os.path.join(TELEGRAM_MESSAGES_PATH, today_str, channel_name)
        os.makedirs(channel_output_dir, exist_ok=True)
        logger.info(f"Saving messages to: {channel_output_dir}")

        # Determine the starting point for scraping (for resuming)
        start_id = get_latest_processed_message_id(channel_output_dir)
        
        # Prepare arguments for iter_messages
        iter_messages_kwargs = {'limit': limit}
        if start_id is not None:
            # If start_id exists, we want messages *older* than this ID.
            # Telethon's max_id parameter means "get messages with ID < max_id".
            iter_messages_kwargs['max_id'] = start_id
            logger.info(f"Resuming scrape for {channel_name} from message ID {start_id} (fetching older messages).")
        else:
            logger.info(f"Starting new scrape for {channel_name}. Limit: {limit if limit is not None else 'None (all messages)'}")

        message_count = 0
        image_count = 0

        # Iterate through messages in the channel, applying the limit and max_id for resuming
        async for message in client.iter_messages(entity, **iter_messages_kwargs):
            message_count += 1
            media_path = None

            # Check for media and download images
            if message.media:
                media_path = await download_media(message, channel_name, message.id)
                if media_path:
                    image_count += 1

            # Prepare message data for JSON storage
            message_data = {
                'id': message.id,
                'date': message.date.isoformat(),
                'message': message.message,
                'sender_id': message.sender_id,
                'channel_id': entity.id,
                'channel_name': channel_name,
                'views': message.views,
                'forwards': message.forwards,
                'replies_count': message.replies.replies if message.replies else 0,
                'has_media': bool(message.media),
                'media_type': type(message.media).__name__ if message.media else None,
                'media_local_path': media_path, # Store local path to downloaded media
                'raw_message_json': message.to_json() # Store full raw message for completeness
            }

            # Save message data as JSON
            message_file_path = os.path.join(channel_output_dir, f"{message.id}.json")
            try:
                with open(message_file_path, 'w', encoding='utf-8') as f:
                    json.dump(message_data, f, ensure_ascii=False, indent=4)
                logger.debug(f"Saved message {message.id} to {message_file_path}")
            except Exception as e:
                logger.error(f"Error saving message {message.id} to JSON: {e}")

        logger.info(f"Finished scraping {channel_name}. Total messages processed in this run: {message_count}, Images downloaded: {image_count}")

    # Corrected RPCError import
    except RPCError as e:
        if "FLOOD_WAIT" in str(e):
            wait_time = int(str(e).split('FLOOD_WAIT_')[1].split(' ')[0])
            logger.warning(f"Rate limit hit for {channel_url}. Waiting for {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            logger.info(f"Resuming scrape for {channel_url} after flood wait.")
        else:
            logger.error(f"Telegram RPC Error for {channel_url}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while scraping {channel_url}: {e}", exc_info=True)

async def main():
    """
    Main function to parse arguments, initialize the Telegram client, and scrape all channels.
    """
    parser = argparse.ArgumentParser(description="Scrape Telegram channel messages and media.")
    parser.add_argument('--limit', type=int, default=None,
                        help='Maximum number of messages to scrape per channel. If not provided, scrapes all messages.')
    args = parser.parse_args()

    if not API_ID or not API_HASH:
        logger.error("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in the .env file.")
        return

    # Initialize Telethon client
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)

    try:
        logger.info("Connecting to Telegram...")
        await client.start()
        logger.info("Connected to Telegram successfully.")

        for channel_url in TELEGRAM_CHANNELS:
            await scrape_channel(client, channel_url, limit=args.limit)

    except Exception as e:
        logger.critical(f"Failed to connect or scrape Telegram: {e}", exc_info=True)
    finally:
        if client.is_connected():
            logger.info("Disconnecting from Telegram.")
            await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
