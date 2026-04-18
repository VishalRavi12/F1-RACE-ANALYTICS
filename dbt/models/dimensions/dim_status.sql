select
    status_id,
    status_description
from {{ ref('stg_status') }}
