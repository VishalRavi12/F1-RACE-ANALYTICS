select
    r.race_id,
    r.season_year,
    r.race_round,
    r.circuit_id,
    c.circuit_name,
    c.circuit_country,
    r.race_name,
    r.race_date,
    r.race_time,
    r.race_url,
    r.fp1_date,
    r.fp1_time,
    r.fp2_date,
    r.fp2_time,
    r.fp3_date,
    r.fp3_time,
    r.quali_date,
    r.quali_time,
    r.sprint_date,
    r.sprint_time
from {{ ref('stg_races') }} as r
left join {{ ref('stg_circuits') }} as c
    on r.circuit_id = c.circuit_id
