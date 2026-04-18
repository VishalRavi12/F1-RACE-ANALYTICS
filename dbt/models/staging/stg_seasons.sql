select
    year as season_year,
    url as season_url
from {{ source('f1_oltp', 'seasons') }}
