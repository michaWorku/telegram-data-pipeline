    -- This test asserts that if a message has media (has_media = TRUE),
    -- then its media_type must not be NULL.
    -- It will return rows (and thus fail the test) if this condition is violated.
    SELECT
        message_id,
        has_media,
        media_type
    FROM
        {{ ref('fct_messages') }}
    WHERE
        has_media = TRUE
        AND media_type IS NULL
    