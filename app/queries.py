try:
    from app.db import run_query
except ModuleNotFoundError:
    from db import run_query


def _in_filter(values: list[str], column: str, param_prefix: str) -> tuple[str, dict]:
    if not values:
        return "", {}

    placeholders = []
    params = {}
    for idx, value in enumerate(values):
        key = f"{param_prefix}_{idx}"
        placeholders.append(f":{key}")
        params[key] = value

    clause = f" and {column} in ({', '.join(placeholders)})"
    return clause, params


def get_year_bounds() -> tuple[int, int]:
    query = """
        with completed_seasons as (
            select season_year
            from mart_driver_constructor_performance
            where season_year < extract(year from current_date)
        )
        select
            min(season_year) as min_year,
            max(season_year) as max_year
        from completed_seasons
    """
    df = run_query(query)
    if df.empty or df.iloc[0]["min_year"] is None or df.iloc[0]["max_year"] is None:
        raise RuntimeError(
            "No completed-season data found in mart_driver_constructor_performance."
        )
    return int(df.iloc[0]["min_year"]), int(df.iloc[0]["max_year"])


def get_driver_options(start_year: int, end_year: int) -> list[str]:
    query = """
        select distinct driver_full_name
        from mart_driver_constructor_performance
        where season_year between :start_year and :end_year
        order by driver_full_name
    """
    df = run_query(query, {"start_year": start_year, "end_year": end_year})
    return df["driver_full_name"].tolist()


def get_constructor_options(start_year: int, end_year: int) -> list[str]:
    query = """
        select distinct constructor_name
        from mart_driver_constructor_performance
        where season_year between :start_year and :end_year
        order by constructor_name
    """
    df = run_query(query, {"start_year": start_year, "end_year": end_year})
    return df["constructor_name"].tolist()


def get_circuit_options(start_year: int, end_year: int) -> list[str]:
    query = """
        select distinct r.circuit_name
        from mart_pitstop_impact p
        inner join dim_race r
            on p.race_id = r.race_id
        where p.season_year between :start_year and :end_year
        order by r.circuit_name
    """
    df = run_query(query, {"start_year": start_year, "end_year": end_year})
    return df["circuit_name"].tolist()


def get_driver_trend_data(
    start_year: int, end_year: int, drivers: list[str]
):
    base_query = """
        select
            season_year,
            driver_full_name,
            sum(total_points) as total_points
        from mart_driver_constructor_performance
        where season_year between :start_year and :end_year
    """
    params = {"start_year": start_year, "end_year": end_year}
    driver_filter, driver_params = _in_filter(
        values=drivers,
        column="driver_full_name",
        param_prefix="driver_name",
    )
    params.update(driver_params)

    query = f"""
        {base_query}
        {driver_filter}
        group by season_year, driver_full_name
        order by season_year, total_points desc
    """
    return run_query(query, params)


def get_constructor_comparison_data(season_year: int, top_n: int):
    query = """
        with constructor_totals as (
            select
                constructor_name,
                sum(total_points) as total_points,
                sum(wins) as wins
            from mart_driver_constructor_performance
            where season_year = :season_year
            group by constructor_name
        )
        select
            constructor_name,
            total_points,
            wins
        from constructor_totals
        order by total_points desc, wins desc
        limit :top_n
    """
    return run_query(query, {"season_year": season_year, "top_n": top_n})


def get_pitstop_impact_data(
    start_year: int,
    end_year: int,
    constructors: list[str],
    circuits: list[str],
):
    params = {"start_year": start_year, "end_year": end_year}
    constructor_filter, constructor_params = _in_filter(
        values=constructors,
        column="c.constructor_name",
        param_prefix="constructor_name",
    )
    circuit_filter, circuit_params = _in_filter(
        values=circuits,
        column="r.circuit_name",
        param_prefix="circuit_name",
    )
    params.update(constructor_params)
    params.update(circuit_params)

    query = f"""
        select
            p.season_year,
            r.race_name,
            r.circuit_name,
            d.driver_full_name,
            c.constructor_name,
            p.pit_stop_count,
            p.total_pit_stop_ms,
            p.adjusted_finish_gain,
            p.points
        from mart_pitstop_impact p
        inner join dim_driver d
            on p.driver_id = d.driver_id
        inner join dim_constructor c
            on p.constructor_id = c.constructor_id
        inner join dim_race r
            on p.race_id = r.race_id
        where p.season_year between :start_year and :end_year
            and p.adjusted_finish_gain is not null
            and p.total_pit_stop_ms is not null
            {constructor_filter}
            {circuit_filter}
        order by p.season_year desc, p.adjusted_finish_gain desc
        limit 5000
    """
    return run_query(query, params)


def get_summary_kpis(start_year: int, end_year: int):
    query = """
        select
            sum(total_points) as total_points,
            sum(wins) as total_wins,
            sum(podiums) as total_podiums,
            count(distinct driver_id) as distinct_drivers,
            count(distinct constructor_id) as distinct_constructors
        from mart_driver_constructor_performance
        where season_year between :start_year and :end_year
    """
    return run_query(query, {"start_year": start_year, "end_year": end_year})


def get_overperformer_leaderboard(
    start_year: int,
    end_year: int,
    constructors: list[str],
    circuits: list[str],
    min_races: int,
    top_n: int,
):
    params = {
        "start_year": start_year,
        "end_year": end_year,
        "min_races": min_races,
        "top_n": top_n,
    }
    constructor_filter, constructor_params = _in_filter(
        values=constructors,
        column="c.constructor_name",
        param_prefix="leaderboard_constructor",
    )
    circuit_filter, circuit_params = _in_filter(
        values=circuits,
        column="r.circuit_name",
        param_prefix="leaderboard_circuit",
    )
    params.update(constructor_params)
    params.update(circuit_params)

    query = f"""
        with base as (
            select
                d.driver_full_name,
                q.qualify_to_finish_delta
            from mart_quali_vs_finish q
            inner join dim_driver d
                on q.driver_id = d.driver_id
            inner join dim_race r
                on q.race_id = r.race_id
            inner join dim_constructor c
                on q.constructor_id = c.constructor_id
            where q.season_year between :start_year and :end_year
                and q.qualify_to_finish_delta is not null
                {constructor_filter}
                {circuit_filter}
        )
        select
            driver_full_name,
            count(*) as races_with_quali_data,
            avg(qualify_to_finish_delta) as avg_finish_gain,
            sum(case when qualify_to_finish_delta > 0 then 1 else 0 end) as gain_races
        from base
        group by driver_full_name
        having count(*) >= :min_races
        order by avg_finish_gain desc, gain_races desc
        limit :top_n
    """
    return run_query(query, params)


def get_race_options(season_year: int):
    query = """
        select
            race_id,
            race_name || ' - ' || circuit_name as race_label
        from dim_race
        where season_year = :season_year
        order by race_round
    """
    return run_query(query, {"season_year": season_year})


def get_race_detail(race_id: int):
    query = """
        select
            d.driver_full_name,
            c.constructor_name,
            f.grid,
            f.position_order as finish_position,
            f.points,
            f.finish_position_delta,
            p.pit_stop_count,
            p.total_pit_stop_ms,
            s.status_description
        from fact_race_results f
        inner join dim_driver d
            on f.driver_id = d.driver_id
        inner join dim_constructor c
            on f.constructor_id = c.constructor_id
        inner join dim_status s
            on f.status_id = s.status_id
        left join mart_pitstop_impact p
            on
                p.race_id = f.race_id
                and p.driver_id = f.driver_id
        where f.race_id = :race_id
        order by
            case when f.position_order is null then 1 else 0 end,
            f.position_order asc,
            f.points desc
    """
    return run_query(query, {"race_id": race_id})
