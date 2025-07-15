-- models/staging/stg_telegram_messages.sql

{{
    config(
        materialized='view',
        schema='staging' 
    )
}}

WITH source_messages AS (
    SELECT
        id,
        channel_id,
        message_date,
        raw_data
    FROM
        {{ source('raw', 'telegram_messages') }}
)

SELECT
    id AS message_id,
    channel_id,
    message_date,
    raw_data AS message_raw_data
FROM
    source_messages
