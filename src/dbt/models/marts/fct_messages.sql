-- models/marts/fct_messages.sql

{{
    config(
        materialized='table',
        schema='analytics'
    )
}}

SELECT
    stg.message_id,
    stg.channel_id,
    TO_CHAR(stg.message_date, 'YYYY-MM-DD') AS date_key, -- Foreign key to dim_dates
    stg.message_date,
    -- Use COALESCE to handle cases where 'message' field might be NULL or missing
    COALESCE(stg.message_raw_data ->> 'message', '') AS message_text,
    (stg.message_raw_data ->> 'media') IS NOT NULL AS has_media,
    stg.message_raw_data ->> 'media_type' AS media_type
FROM
    {{ ref('stg_telegram_messages') }} stg
