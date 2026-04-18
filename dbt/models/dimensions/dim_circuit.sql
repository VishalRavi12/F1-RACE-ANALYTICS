select
    circuit_id,
    circuit_ref,
    circuit_name,
    circuit_location,
    circuit_country,
    circuit_latitude,
    circuit_longitude,
    circuit_altitude,
    circuit_url
from {{ ref('stg_circuits') }}
