select
    driver_id,
    driver_ref,
    number as driver_number,
    code as driver_code,
    forename as driver_forename,
    surname as driver_surname,
    dob as driver_date_of_birth,
    nationality as driver_nationality,
    url as driver_url
from {{ source('f1_oltp', 'drivers') }}
