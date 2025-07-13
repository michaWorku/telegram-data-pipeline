{{ config(materialized='table', schema='analytics') }}

WITH date_range AS (
    SELECT
        MIN(message_date::DATE) AS min_date,
        MAX(message_date::DATE) AS max_date
    FROM
        {{ ref('stg_telegram_messages') }}
),

date_series AS (
    SELECT generate_series(min_date, max_date, '1 day'::interval) AS date_day
    FROM date_range
)

SELECT
    date_day AS date_key,
    EXTRACT(YEAR FROM date_day) AS year,
    EXTRACT(MONTH FROM date_day) AS month,
    TO_CHAR(date_day, 'Month') AS month_name,
    EXTRACT(DAY FROM date_day) AS day_of_month,
    EXTRACT(DOW FROM date_day) AS day_of_week, -- 0 = Sunday, 6 = Saturday
    TO_CHAR(date_day, 'Day') AS day_name,
    EXTRACT(DOY FROM date_day) AS day_of_year,
    EXTRACT(WEEK FROM date_day) AS week_of_year,
    EXTRACT(QUARTER FROM date_day) AS quarter,
    TO_CHAR(date_day, 'YYYY-MM') AS year_month,
    (EXTRACT(DOW FROM date_day) IN (0, 6)) AS is_weekend -- Boolean for weekend
FROM
    date_series
ORDER BY
    date_day
