from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Schema for the "Top Products" report response
class TopProduct(BaseModel):
    product_name: str
    mention_count: int

# Schema for the "Channel Activity" report response
class ChannelActivity(BaseModel):
    date: str # YYYY-MM-DD format
    message_count: int

# Schema for individual message search results
class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_date: datetime
    message_text: str
    has_media: bool
    media_type: Optional[str] = None # Optional as it can be NULL

# Generic error response schema
class ErrorResponse(BaseModel):
    detail: str

