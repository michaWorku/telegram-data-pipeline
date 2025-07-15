from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import psycopg2.extensions # For type hinting the connection
from contextlib import asynccontextmanager

from .database import get_db # Relative import
from .schemas import TopProduct, ChannelActivity, MessageSearchResult, ErrorResponse # Relative import
from .crud import get_top_products, get_channel_activity, search_messages # Relative import

# --- FastAPI Application Lifecycle (Optional, but good for cleanup) ---
# This context manager can be used for startup/shutdown events,
# though for simple psycopg2 connections, it's not strictly necessary here.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: You could add database connection pool initialization here if needed
    print("FastAPI application starting up...")
    yield
    # Shutdown: You could add database connection pool shutdown here
    print("FastAPI application shutting down.")

app = FastAPI(
    title="Telegram Data Analytics API",
    description="API to query transformed Telegram channel data.",
    version="1.0.0",
    lifespan=lifespan # Assign the lifespan context manager
)

# --- API Endpoints ---

@app.get(
    "/api/reports/top-products",
    response_model=List[TopProduct],
    summary="Get top mentioned products",
    description="Returns a list of the most frequently mentioned product-related keywords in messages.",
    responses={200: {"description": "Successful Response"}, 500: {"model": ErrorResponse, "description": "Internal Server Error"}}
)
async def read_top_products(
    limit: int = Query(10, ge=1, le=100, description="Number of top products to return"),
    db_conn: psycopg2.extensions.connection = Depends(get_db)
):
    try:
        products = get_top_products(db_conn, limit)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve top products: {e}")

@app.get(
    "/api/channels/{channel_name}/activity",
    response_model=List[ChannelActivity],
    summary="Get channel posting activity",
    description="Returns the daily message posting activity for a specific Telegram channel.",
    responses={200: {"description": "Successful Response"}, 404: {"model": ErrorResponse, "description": "Channel not found"}, 500: {"model": ErrorResponse, "description": "Internal Server Error"}}
)
async def read_channel_activity(
    channel_name: str,
    db_conn: psycopg2.extensions.connection = Depends(get_db)
):
    try:
        activity = get_channel_activity(db_conn, channel_name)
        if not activity:
            # You might want a more sophisticated check if the channel exists but has no activity
            # For now, if no activity, assume channel name might be wrong or no data
            raise HTTPException(status_code=404, detail=f"No activity found for channel '{channel_name}'. Check channel name or data availability.")
        return activity
    except HTTPException as e:
        raise e # Re-raise HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve channel activity: {e}")

@app.get(
    "/api/search/messages",
    response_model=List[MessageSearchResult],
    summary="Search messages by keyword",
    description="Searches for Telegram messages containing a specific keyword.",
    responses={200: {"description": "Successful Response"}, 500: {"model": ErrorResponse, "description": "Internal Server Error"}}
)
async def search_telegram_messages(
    query: str = Query(..., min_length=1, description="Keyword to search for in message text"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of messages to return"),
    db_conn: psycopg2.extensions.connection = Depends(get_db)
):
    try:
        messages = search_messages(db_conn, query, limit)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search messages: {e}")

