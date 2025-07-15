-- models/marts/fct_image_detections.sql

{{
    config(
        materialized='table',
        schema='analytics'
    )
}}

SELECT
    det.id AS detection_id,
    det.message_id,
    det.image_path,
    det.detected_object_class,
    det.confidence_score,
    det.detection_timestamp
FROM
    {{ source('raw', 'image_detections') }} AS det
-- Optional: INNER JOIN with fct_messages if you want to only include detections
-- that have a corresponding message in fct_messages, which would fix the relationships test
-- if the data inconsistency is acceptable.
-- INNER JOIN {{ ref('fct_messages') }} AS msg
--   ON det.message_id = msg.message_id
