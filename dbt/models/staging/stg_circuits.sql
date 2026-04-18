select
    circuit_id,
    circuit_ref,
    name as circuit_name,
    location as circuit_location,
    country as circuit_country,
    lat as circuit_latitude,
    lng as circuit_longitude,
    alt as circuit_altitude,
    url as circuit_url
from {{ source('f1_oltp', 'circuits') }}
