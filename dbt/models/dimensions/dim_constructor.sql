select
    constructor_id,
    constructor_ref,
    constructor_name,
    constructor_nationality,
    constructor_url
from {{ ref('stg_constructors') }}
