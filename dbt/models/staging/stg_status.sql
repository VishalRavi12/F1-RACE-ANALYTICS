select
    status_id,
    status as status_description
from {{ source('f1_oltp', 'status') }}
