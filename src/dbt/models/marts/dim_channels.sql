{{ config(materialized='table', schema='analytics') }}

SELECT
    channel_id,
    channel_name,
    MIN(message_date) AS first_message_date,
    MAX(message_date) AS last_message_date,
    COUNT(DISTINCT message_id) AS total_messages
FROM
    {{ ref('stg_telegram_messages') }}
WHERE
    channel_id IS NOT NULL
GROUP BY
    channel_id,
    channel_name
