import altair as alt
import streamlit as st

try:
    from app.queries import (
        get_circuit_options,
        get_constructor_comparison_data,
        get_constructor_options,
        get_driver_options,
        get_driver_trend_data,
        get_overperformer_leaderboard,
        get_pitstop_impact_data,
        get_race_detail,
        get_race_options,
        get_summary_kpis,
        get_year_bounds,
    )
except ModuleNotFoundError:
    from queries import (
        get_circuit_options,
        get_constructor_comparison_data,
        get_constructor_options,
        get_driver_options,
        get_driver_trend_data,
        get_overperformer_leaderboard,
        get_pitstop_impact_data,
        get_race_detail,
        get_race_options,
        get_summary_kpis,
        get_year_bounds,
    )

st.set_page_config(
    page_title="F1 Race Analytics",
    page_icon="F1",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #f5f0e6 0%, #f8f8f8 45%, #ffffff 100%);
    }
    .main-title {
        font-size: 2.0rem;
        font-weight: 700;
        color: #8c2f39;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        color: #3d3d3d;
        margin-bottom: 1.0rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">F1 Race Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Live analytics from Neon PostgreSQL via dbt marts.</div>',
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False, ttl=1800)
def cached_get_year_bounds():
    return get_year_bounds()


@st.cache_data(show_spinner=False, ttl=1800)
def cached_get_driver_options(start_year: int, end_year: int):
    return get_driver_options(start_year, end_year)


@st.cache_data(show_spinner=False, ttl=1800)
def cached_get_constructor_options(start_year: int, end_year: int):
    return get_constructor_options(start_year, end_year)


@st.cache_data(show_spinner=False, ttl=1800)
def cached_get_circuit_options(start_year: int, end_year: int):
    return get_circuit_options(start_year, end_year)


@st.cache_data(show_spinner=True, ttl=900)
def cached_driver_trends(start_year: int, end_year: int, drivers: tuple[str, ...]):
    return get_driver_trend_data(start_year, end_year, list(drivers))


@st.cache_data(show_spinner=True, ttl=900)
def cached_constructor_comparison(season_year: int, top_n: int):
    return get_constructor_comparison_data(season_year, top_n)


@st.cache_data(show_spinner=True, ttl=900)
def cached_pitstop_impact(
    start_year: int,
    end_year: int,
    constructors: tuple[str, ...],
    circuits: tuple[str, ...],
):
    return get_pitstop_impact_data(start_year, end_year, list(constructors), list(circuits))


@st.cache_data(show_spinner=True, ttl=900)
def cached_summary_kpis(start_year: int, end_year: int):
    return get_summary_kpis(start_year, end_year)


@st.cache_data(show_spinner=True, ttl=900)
def cached_overperformers(
    start_year: int,
    end_year: int,
    constructors: tuple[str, ...],
    circuits: tuple[str, ...],
    min_races: int,
    top_n: int,
):
    return get_overperformer_leaderboard(
        start_year,
        end_year,
        list(constructors),
        list(circuits),
        min_races,
        top_n,
    )


@st.cache_data(show_spinner=False, ttl=900)
def cached_race_options(season_year: int):
    return get_race_options(season_year)


@st.cache_data(show_spinner=True, ttl=900)
def cached_race_detail(race_id: int):
    return get_race_detail(race_id)


try:
    min_year, max_year = cached_get_year_bounds()
except Exception as exc:
    st.error(f"Unable to load data from database: {exc}")
    st.stop()

with st.sidebar:
    st.header("Filters")

    selected_year_range = st.slider(
        "Season Range",
        min_value=min_year,
        max_value=max_year,
        value=(max(min_year, max_year - 10), max_year),
    )
    start_year, end_year = selected_year_range

    driver_options = cached_get_driver_options(start_year, end_year)
    default_driver_selection = driver_options[:4] if len(driver_options) >= 4 else driver_options
    selected_drivers = st.multiselect(
        "Drivers",
        options=driver_options,
        default=default_driver_selection,
    )

    constructor_options = cached_get_constructor_options(start_year, end_year)
    selected_constructors = st.multiselect(
        "Constructors (Pit Stop Chart)",
        options=constructor_options,
        default=[],
    )

    circuit_options = cached_get_circuit_options(start_year, end_year)
    selected_circuits = st.multiselect(
        "Circuits (Pit Stop Chart)",
        options=circuit_options,
        default=[],
    )

    season_for_constructor_chart = st.selectbox(
        "Season for Constructor Ranking",
        options=list(range(end_year, start_year - 1, -1)),
    )
    top_n_constructors = st.slider(
        "Top Constructors",
        min_value=5,
        max_value=20,
        value=10,
    )

    st.divider()
    st.subheader("Advanced Views")
    min_races_for_leaderboard = st.slider(
        "Min Races for Overperformer Leaderboard",
        min_value=3,
        max_value=30,
        value=8,
    )
    top_n_overperformers = st.slider(
        "Top Overperformers",
        min_value=5,
        max_value=25,
        value=12,
    )
    race_detail_season = st.selectbox(
        "Race Detail Season",
        options=list(range(end_year, start_year - 1, -1)),
    )

driver_trends_df = cached_driver_trends(start_year, end_year, tuple(selected_drivers))
constructor_comparison_df = cached_constructor_comparison(
    season_for_constructor_chart, top_n_constructors
)
pitstop_impact_df = cached_pitstop_impact(
    start_year,
    end_year,
    tuple(selected_constructors),
    tuple(selected_circuits),
)
kpi_df = cached_summary_kpis(start_year, end_year)
overperformer_df = cached_overperformers(
    start_year,
    end_year,
    tuple(selected_constructors),
    tuple(selected_circuits),
    min_races_for_leaderboard,
    top_n_overperformers,
)
race_options_df = cached_race_options(race_detail_season)
selected_race_id = None
if not race_options_df.empty:
    race_labels = race_options_df["race_label"].tolist()
    race_lookup = dict(zip(race_labels, race_options_df["race_id"].tolist()))
    selected_race_label = st.selectbox(
        "Race Drill-Down",
        options=race_labels,
        help="Inspect one race in detail (grid, finish, points, pit stops).",
    )
    selected_race_id = race_lookup[selected_race_label]

if kpi_df.empty:
    st.warning("No KPI data for selected season range.")
else:
    kpi_row = kpi_df.iloc[0]
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Points", f"{int(kpi_row['total_points'] or 0):,}")
    k2.metric("Total Wins", f"{int(kpi_row['total_wins'] or 0):,}")
    k3.metric("Total Podiums", f"{int(kpi_row['total_podiums'] or 0):,}")
    k4.metric("Drivers", f"{int(kpi_row['distinct_drivers'] or 0):,}")
    k5.metric("Constructors", f"{int(kpi_row['distinct_constructors'] or 0):,}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Driver Points Trend by Season")
    if driver_trends_df.empty:
        st.warning("No driver trend data for the selected filters.")
    else:
        trend_chart = (
            alt.Chart(driver_trends_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("season_year:O", title="Season"),
                y=alt.Y("total_points:Q", title="Total Points"),
                color=alt.Color("driver_full_name:N", title="Driver"),
                tooltip=["season_year", "driver_full_name", "total_points"],
            )
            .properties(height=360)
        )
        st.altair_chart(trend_chart, use_container_width=True)

with col2:
    st.subheader(f"Top {top_n_constructors} Constructors in {season_for_constructor_chart}")
    if constructor_comparison_df.empty:
        st.warning("No constructor comparison data for the selected season.")
    else:
        constructor_chart = (
            alt.Chart(constructor_comparison_df)
            .mark_bar()
            .encode(
                x=alt.X("total_points:Q", title="Total Points"),
                y=alt.Y("constructor_name:N", sort="-x", title="Constructor"),
                color=alt.Color("wins:Q", title="Wins"),
                tooltip=["constructor_name", "total_points", "wins"],
            )
            .properties(height=360)
        )
        st.altair_chart(constructor_chart, use_container_width=True)

st.subheader("Qualifying Overperformer Leaderboard")
if overperformer_df.empty:
    st.warning("No overperformer data for selected filters.")
else:
    leaderboard_chart = (
        alt.Chart(overperformer_df)
        .mark_bar()
        .encode(
            x=alt.X("avg_finish_gain:Q", title="Average Finish Gain vs Qualifying"),
            y=alt.Y("driver_full_name:N", sort="-x", title="Driver"),
            color=alt.Color("gain_races:Q", title="Races with Gain"),
            tooltip=[
                "driver_full_name",
                "races_with_quali_data",
                "avg_finish_gain",
                "gain_races",
            ],
        )
        .properties(height=380)
    )
    st.altair_chart(leaderboard_chart, use_container_width=True)

if selected_race_id is not None:
    st.subheader("Race Detail Table")
    race_detail_df = cached_race_detail(int(selected_race_id))
    if race_detail_df.empty:
        st.warning("No race detail data found for selected race.")
    else:
        st.dataframe(
            race_detail_df,
            use_container_width=True,
            hide_index=True,
        )

st.divider()
st.subheader("Strategy Deep Dive: Pit Stop Time vs Finish Gain")
if pitstop_impact_df.empty:
    st.warning("No pit stop impact data for the selected filters.")
else:
    pitstop_chart = (
        alt.Chart(pitstop_impact_df)
        .mark_circle(size=80, opacity=0.65)
        .encode(
            x=alt.X("total_pit_stop_ms:Q", title="Total Pit Stop Time (ms)"),
            y=alt.Y("adjusted_finish_gain:Q", title="Adjusted Finish Gain"),
            color=alt.Color("constructor_name:N", title="Constructor"),
            tooltip=[
                "season_year",
                "race_name",
                "circuit_name",
                "driver_full_name",
                "constructor_name",
                "pit_stop_count",
                "total_pit_stop_ms",
                "adjusted_finish_gain",
                "points",
            ],
        )
        .properties(height=360)
        .interactive()
    )
    st.altair_chart(pitstop_chart, use_container_width=True)

st.caption(
    "Data source: Neon PostgreSQL (live), transformed by dbt models and marts."
)
