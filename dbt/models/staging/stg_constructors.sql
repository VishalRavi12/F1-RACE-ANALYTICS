select
    constructor_id,
    constructor_ref,
    name as constructor_name,
    nationality as constructor_nationality,
    url as constructor_url
from {{ source('f1_oltp', 'constructors') }}
