-- models/marts/dim_dates.sql

{{
    config(
        materialized='table',
        schema='analytics'
    )
}}

WITH date_series AS (
    -- Generate dates from the start of 2021 to the end of 2025
    SELECT generate_series('2021-01-01'::date, '2025-12-31'::date, '1 day'::interval) as date_day -- <-- CHANGED START DATE
)

SELECT
    TO_CHAR(date_day, 'YYYY-MM-DD') AS date_key,
    date_day AS full_date,
    EXTRACT(YEAR FROM date_day) AS year,
    EXTRACT(MONTH FROM date_day) AS month,
    TO_CHAR(date_day, 'Month') AS month_name,
    EXTRACT(DAY FROM date_day) AS day_of_month,
    EXTRACT(DOW FROM date_day) AS day_of_week, -- 0=Sunday, 6=Saturday
    TO_CHAR(date_day, 'Day') AS day_name,
    EXTRACT(DOY FROM date_day) AS day_of_year,
    EXTRACT(WEEK FROM date_day) AS week_of_year,
    EXTRACT(QUARTER FROM date_day) AS quarter,
    (EXTRACT(ISODOW FROM date_day) IN (6, 7)) AS is_weekend, -- ISO DOW: 1=Monday, 7=Sunday
    TO_CHAR(date_day, 'YYYY-MM') AS year_month
FROM
    date_series
