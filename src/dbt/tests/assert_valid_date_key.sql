    -- This test asserts that all date_key values in dim_dates are valid dates.
    -- It will return rows (and thus fail the test) if a date_key cannot be cast to a date.
    SELECT
        date_key
    FROM
        {{ ref('dim_dates') }}
    WHERE
        date_key::date IS NULL
    