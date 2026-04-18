select
    driver_id,
    driver_ref,
    driver_number,
    driver_code,
    driver_forename,
    driver_surname,
    driver_date_of_birth,
    driver_nationality,
    driver_url,
    concat(driver_forename, ' ', driver_surname) as driver_full_name
from {{ ref('stg_drivers') }}
