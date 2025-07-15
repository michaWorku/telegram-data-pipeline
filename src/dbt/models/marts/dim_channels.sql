-- models/marts/dim_channels.sql

{{
    config(
        materialized='table',
        schema='analytics'
    )
}}

SELECT
    DISTINCT channel_id,
    -- Extract channel name from message_raw_data
    COALESCE(
        (message_raw_data ->> 'peer_id')::text,
        'Unknown Channel'
    ) AS channel_name
FROM
    {{ ref('stg_telegram_messages') }}
