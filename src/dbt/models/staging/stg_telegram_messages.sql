{{ config(materialized='view', schema='staging') }}

WITH source_data AS (
    SELECT
        id AS message_id,
        channel_id,
        message_date,
        raw_data ->> 'message' AS message_text,
        raw_data ->> 'sender_id' AS sender_id,
        raw_data ->> 'channel_name' AS channel_name,
        (raw_data ->> 'views')::BIGINT AS views,
        (raw_data ->> 'forwards')::BIGINT AS forwards,
        (raw_data ->> 'replies_count')::BIGINT AS replies_count,
        (raw_data ->> 'has_media')::BOOLEAN AS has_media,
        raw_data ->> 'media_type' AS media_type,
        raw_data ->> 'media_local_path' AS media_local_path,
        load_timestamp
    FROM
        {{ source('raw', 'telegram_messages') }}
)

SELECT
    message_id,
    channel_id,
    message_date,
    message_text,
    sender_id,
    channel_name,
    views,
    forwards,
    replies_count,
    has_media,
    media_type,
    media_local_path,
    load_timestamp,
    -- Add a simple metric: message length
    LENGTH(message_text) AS message_length_chars
FROM
    source_data
WHERE
    message_id IS NOT NULL -- Ensure primary key is not null
    AND message_text IS NOT NULL -- Only process messages with text content
