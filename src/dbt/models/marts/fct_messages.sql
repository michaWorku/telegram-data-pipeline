{{ config(materialized='table', schema='analytics') }}

SELECT
    stg.message_id,
    stg.channel_id,
    dc.channel_name, -- From dim_channels
    stg.message_date,
    dd.date_key, -- From dim_dates
    stg.message_text,
    stg.sender_id,
    stg.views,
    stg.forwards,
    stg.replies_count,
    stg.has_media,
    stg.media_type,
    stg.media_local_path,
    stg.message_length_chars,
    stg.load_timestamp
FROM
    {{ ref('stg_telegram_messages') }} stg
LEFT JOIN
    {{ ref('dim_channels') }} dc ON stg.channel_id = dc.channel_id
LEFT JOIN
    {{ ref('dim_dates') }} dd ON stg.message_date::DATE = dd.date_key
WHERE
    stg.message_id IS NOT NULL
