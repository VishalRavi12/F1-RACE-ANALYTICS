select
    race_id,
    driver_id,
    stop as stop_number,
    lap,
    time as stop_time,
    duration as stop_duration,
    milliseconds as stop_milliseconds
from {{ source('f1_oltp', 'pit_stops') }}
