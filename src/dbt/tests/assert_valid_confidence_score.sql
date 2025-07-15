-- This test asserts that confidence_score in fct_image_detections is between 0.0 and 1.0.
-- It will return rows (and thus fail the test) if the score is outside this range.
SELECT
    detection_id,
    confidence_score
FROM
    {{ ref('fct_image_detections') }}
WHERE
    confidence_score < 0.0 OR confidence_score > 1.0
