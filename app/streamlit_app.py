import altair as alt
import pandas as pd
import streamlit as st

try:
    from app.queries import (
        get_circuit_options,
        get_constructor_comparison_data,
        get_constructor_final_points_table,
        get_constructor_options,
        get_driver_final_points_table,
        get_driver_options,
        get_driver_trend_data,
        get_overperformer_leaderboard,
        get_pitstop_impact_data,
        get_race_detail,
        get_race_options,
        get_summary_kpis,
        get_team_historic_trend,
        get_track_historic_winners,
        get_year_bounds,
    )
except ModuleNotFoundError:
    from queries import (
        get_circuit_options,
        get_constructor_comparison_data,
        get_constructor_final_points_table,
        get_constructor_options,
        get_driver_final_points_table,
        get_driver_options,
        get_driver_trend_data,
        get_overperformer_leaderboard,
        get_pitstop_impact_data,
        get_race_detail,
        get_race_options,
        get_summary_kpis,
        get_team_historic_trend,
        get_track_historic_winners,
        get_year_bounds,
    )

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="F1 Race Analytics",
    page_icon="F1",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    :root {
        --red: #e10600;
        --red-dark: #b30500;
        --ink: #15151a;
        --ink-2: #2d2d35;
        --muted: #6b7080;
        --subtle: #9ca3af;
        --bg: #ffffff;
        --bg-2: #f8f9fb;
        --border: #e5e7eb;
        --card: #ffffff;
    }

    /* ── base ── */
    .stApp {
        font-family: "Inter", -apple-system, sans-serif;
        color: var(--ink);
        background: var(--bg);
    }

    /* ── sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--bg-2);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--ink);
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.3rem;
    }

    /* ── metrics ── */
    [data-testid="stMetric"] {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.6rem 0.9rem;
    }
    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-weight: 700;
    }

    /* ── tabs ── */
    [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid var(--border);
        margin-bottom: 1rem;
    }
    button[role="tab"] {
        border-radius: 0 !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        background: transparent !important;
        color: var(--muted) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 1.1rem !important;
        margin-bottom: -2px !important;
        transition: all 0.15s ease !important;
    }
    button[role="tab"]:hover {
        color: var(--ink) !important;
    }
    button[role="tab"][aria-selected="true"] {
        background: transparent !important;
        border-bottom: 2px solid var(--red) !important;
        color: var(--red) !important;
    }

    /* ── hero header ── */
    .hero-shell {
        background: var(--bg);
        border-bottom: 1px solid var(--border);
        padding: 0.8rem 0 0.6rem 0;
        margin-bottom: 0.6rem;
    }
    .hero-kicker {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--red);
        font-weight: 700;
        margin-bottom: 0.15rem;
    }
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--ink);
        margin-bottom: 0;
        letter-spacing: -0.5px;
    }
    .subtitle {
        color: var(--muted);
        font-size: 0.9rem;
        margin-bottom: 0;
    }

    /* ── section headers ── */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--ink);
        border-left: 3px solid var(--red);
        padding-left: 0.55rem;
        margin-bottom: 0.25rem;
    }

    /* ── descriptions ── */
    .section-desc {
        color: var(--muted);
        font-size: 0.85rem;
        margin-bottom: 0.75rem;
        line-height: 1.6;
    }

    /* ── expanders ── */
    details[data-testid="stExpander"] {
        background: var(--card);
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* ── dividers ── */
    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 0.75rem 0;
    }

    /* ── footer ── */
    .footer-bar {
        text-align: center;
        color: var(--subtle);
        font-size: 0.76rem;
        padding: 1rem 0 0.5rem 0;
        border-top: 1px solid var(--border);
        margin-top: 1.5rem;
    }
    .footer-bar b {
        color: var(--muted);
    }

    /* ── alerts ── */
    [data-testid="stAlert"] {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Cached query wrappers
# ---------------------------------------------------------------------------

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
def cached_summary_kpis(start_year: int, end_year: int):
    return get_summary_kpis(start_year, end_year)


@st.cache_data(show_spinner=True, ttl=900)
def cached_driver_trends(start_year: int, end_year: int, drivers: tuple[str, ...]):
    return get_driver_trend_data(start_year, end_year, list(drivers))


@st.cache_data(show_spinner=True, ttl=900)
def cached_constructor_comparison(season_year: int, top_n: int):
    return get_constructor_comparison_data(season_year, top_n)


@st.cache_data(show_spinner=True, ttl=900)
def cached_driver_final_points(season_year: int, top_n: int):
    return get_driver_final_points_table(season_year, top_n)


@st.cache_data(show_spinner=True, ttl=900)
def cached_constructor_final_points(season_year: int, top_n: int):
    return get_constructor_final_points_table(season_year, top_n)


@st.cache_data(show_spinner=True, ttl=900)
def cached_team_historic(start_year: int, end_year: int, constructors: tuple[str, ...]):
    return get_team_historic_trend(start_year, end_year, list(constructors))


@st.cache_data(show_spinner=True, ttl=900)
def cached_track_historic(start_year: int, end_year: int, circuit_name: str):
    return get_track_historic_winners(start_year, end_year, circuit_name)


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
        start_year, end_year, list(constructors), list(circuits), min_races, top_n,
    )


@st.cache_data(show_spinner=True, ttl=900)
def cached_pitstop_impact(
    start_year: int,
    end_year: int,
    constructors: tuple[str, ...],
    circuits: tuple[str, ...],
):
    return get_pitstop_impact_data(start_year, end_year, list(constructors), list(circuits))


@st.cache_data(show_spinner=False, ttl=900)
def cached_race_options(season_year: int):
    return get_race_options(season_year)


@st.cache_data(show_spinner=True, ttl=900)
def cached_race_detail(race_id: int):
    return get_race_detail(race_id)


F1_PALETTE = [
    "#e10600",  # F1 red
    "#1e3a5f",  # navy
    "#f5a623",  # amber
    "#00a651",  # green
    "#7b2d8e",  # purple
    "#2196f3",  # blue
    "#ff6f00",  # deep orange
    "#00897b",  # teal
    "#546e7a",  # blue-grey
    "#c62828",  # dark red
    "#283593",  # indigo
    "#ef6c00",  # orange
]


def polish_chart(chart: alt.Chart) -> alt.Chart:
    return (
        chart.configure_view(strokeOpacity=0)
        .configure_range(category=F1_PALETTE)
        .configure_axis(
            labelColor="#6b7080",
            titleColor="#2d2d35",
            gridColor="#f0f0f3",
            domainColor="#e5e7eb",
            labelFontSize=11,
            titleFontSize=12,
            labelFont="Inter, sans-serif",
            titleFont="Inter, sans-serif",
        )
        .configure_legend(
            labelColor="#6b7080",
            titleColor="#2d2d35",
            orient="bottom",
            labelFontSize=11,
            titleFontSize=12,
            padding=10,
            labelFont="Inter, sans-serif",
            titleFont="Inter, sans-serif",
            symbolSize=80,
        )
        .configure_title(
            color="#15151a",
            anchor="start",
            fontSize=13,
            font="Inter, sans-serif",
            fontWeight=600,
        )
    )


# ---------------------------------------------------------------------------
# Bootstrap — year bounds
# ---------------------------------------------------------------------------
try:
    min_year, max_year = cached_get_year_bounds()
except Exception as exc:
    st.error(f"Unable to load data from database: {exc}")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar — global filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div style="text-align:center; padding: 0.2rem 0 0.4rem 0;">'
        '<span style="font-weight: 800; font-size: 1.3rem; color: #e10600;">F1</span>'
        '<span style="font-size: 0.72rem; color: #6b7080; margin-left: 0.3rem; '
        'letter-spacing: 0.06em; text-transform: uppercase; font-weight: 600;">Race Analytics</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("### Filters")
    global_start_year, global_end_year = st.slider(
        "Season range",
        min_value=min_year,
        max_value=max_year,
        value=(max(min_year, max_year - 10), max_year),
    )

    driver_options = cached_get_driver_options(global_start_year, global_end_year)
    constructor_options = cached_get_constructor_options(global_start_year, global_end_year)
    circuit_options = cached_get_circuit_options(global_start_year, global_end_year)

    st.caption(
        f"Showing data for **{global_start_year}** – **{global_end_year}** "
        f"({global_end_year - global_start_year + 1} seasons)"
    )
    st.divider()
    st.markdown(
        "**Data source:** Neon PostgreSQL (live) \n\n"
        "**Transform:** dbt star-schema marts \n\n"
        "**Deploy:** Render (auto-deploy)"
    )

# ---------------------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="hero-shell">'
    '<div class="hero-kicker">Formula 1 Performance Intelligence</div>'
    '<div class="main-title">F1 Race Analytics</div>'
    '<div class="subtitle">'
    'Interactive dashboard powered by live Neon PostgreSQL queries and dbt marts.'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Aggregate numbers across all races in the selected season range. "
    "Adjust the range in the sidebar to update."
)

kpi_df = cached_summary_kpis(global_start_year, global_end_year)
if not kpi_df.empty:
    row = kpi_df.iloc[0]
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Points", f"{int(row['total_points'] or 0):,}")
    k2.metric("Total Wins", f"{int(row['total_wins'] or 0):,}")
    k3.metric("Total Podiums", f"{int(row['total_podiums'] or 0):,}")
    k4.metric("Drivers", f"{int(row['distinct_drivers'] or 0):,}")
    k5.metric("Constructors", f"{int(row['distinct_constructors'] or 0):,}")

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_perf, tab_strategy, tab_standings, tab_tracks, tab_races = st.tabs([
    "Performance Trends",
    "Strategy & Overperformers",
    "Season Standings",
    "Circuits & History",
    "Race Explorer",
])

# ── Tab 1: Performance Trends ─────────────────────────────────────────────
with tab_perf:
    st.markdown('<p class="section-desc">'
                'Compare driver and constructor performance across seasons.'
                '</p>', unsafe_allow_html=True)

    # Driver points trend
    st.markdown('<div class="section-header">Driver Points Trend</div>', unsafe_allow_html=True)
    st.caption(
        "Total championship points scored by each driver per season. "
        "Use the multiselect below to compare specific drivers side by side — "
        "rising lines indicate improving seasons, peaks often mark title-winning years."
    )
    preferred_drivers = ["Lewis Hamilton", "Max Verstappen"]
    trend_default = [d for d in preferred_drivers if d in driver_options]
    if not trend_default:
        trend_default = driver_options[:5] if len(driver_options) >= 5 else driver_options
    trend_drivers = st.multiselect(
        "Select drivers",
        options=driver_options,
        default=trend_default,
        key="trend_drivers",
    )
    driver_trends_df = cached_driver_trends(
        global_start_year, global_end_year, tuple(trend_drivers),
    )
    if driver_trends_df.empty:
        st.info("No driver trend data for the selected filters.")
    else:
        base = alt.Chart(driver_trends_df).encode(
            x=alt.X("season_year:O", title="Season"),
            y=alt.Y("total_points:Q", title="Points"),
            color=alt.Color("driver_full_name:N", title="Driver"),
        )
        trend_chart = (
            base.mark_line(strokeWidth=2.5)
            + base.mark_circle(size=50)
        ).encode(
            tooltip=["season_year", "driver_full_name", "total_points"],
        ).properties(height=370).interactive()
        st.altair_chart(polish_chart(trend_chart), use_container_width=True)

    st.divider()

    # Constructor + Team historic side by side
    col_cc, col_th = st.columns(2)

    with col_cc:
        st.markdown('<div class="section-header">Constructor Comparison</div>', unsafe_allow_html=True)
        st.caption(
            "Total points and race wins for each constructor (team) in a single season. "
            "Bar length shows points; color intensity shows win count — darker bars indicate "
            "teams that converted points into victories."
        )
        cc_season = st.selectbox(
            "Season",
            options=list(range(global_end_year, global_start_year - 1, -1)),
            key="cc_season",
        )
        cc_top_n = st.slider("Top N", 5, 20, 10, key="cc_top_n")
        constructor_df = cached_constructor_comparison(cc_season, cc_top_n)
        if constructor_df.empty:
            st.info("No data for this season.")
        else:
            cc_chart = (
                alt.Chart(constructor_df)
                .mark_bar(cornerRadiusEnd=4)
                .encode(
                    x=alt.X("total_points:Q", title="Points"),
                    y=alt.Y("constructor_name:N", sort="-x", title=""),
                    color=alt.Color(
                        "wins:Q",
                        title="Wins",
                        scale=alt.Scale(scheme="reds"),
                    ),
                    tooltip=["constructor_name", "total_points", "wins"],
                )
                .properties(height=340)
            )
            st.altair_chart(polish_chart(cc_chart), use_container_width=True)

    with col_th:
        st.markdown('<div class="section-header">Team Historic Trend</div>', unsafe_allow_html=True)
        st.caption(
            "Constructor points over multiple seasons. Useful for spotting dominance eras — "
            "e.g. Ferrari in the early 2000s, Red Bull 2010-2013, or Mercedes 2014-2020."
        )
        team_range = st.slider(
            "Season range",
            min_value=global_start_year,
            max_value=global_end_year,
            value=(max(global_start_year, global_end_year - 10), global_end_year),
            key="team_range",
        )
        selected_teams = st.multiselect(
            "Select constructors",
            options=constructor_options,
            default=constructor_options[:5] if len(constructor_options) >= 5 else constructor_options,
            key="team_constructors",
        )
        team_df = cached_team_historic(team_range[0], team_range[1], tuple(selected_teams))
        if team_df.empty:
            st.info("No team data for selected filters.")
        else:
            t_base = alt.Chart(team_df).encode(
                x=alt.X("season_year:O", title="Season"),
                y=alt.Y("total_points:Q", title="Points"),
                color=alt.Color("constructor_name:N", title="Constructor"),
            )
            team_chart = (
                t_base.mark_line(strokeWidth=2.5)
                + t_base.mark_circle(size=45)
            ).encode(
                tooltip=["season_year", "constructor_name", "total_points", "wins"],
            ).properties(height=340).interactive()
            st.altair_chart(polish_chart(team_chart), use_container_width=True)


# ── Tab 2: Strategy & Overperformers ──────────────────────────────────────
with tab_strategy:
    st.markdown('<p class="section-desc">'
                'Analyze qualifying-to-finish gains and pit stop strategy impact.'
                '</p>', unsafe_allow_html=True)

    # Overperformer leaderboard
    st.markdown('<div class="section-header">Qualifying Overperformer Leaderboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-desc">'
        "In F1, qualifying determines the starting grid. Some drivers consistently "
        "finish higher than where they qualified — these are <b>overperformers</b>. "
        "This chart ranks drivers by their <b>average positions gained</b> from qualifying "
        "to the chequered flag. A value of +3.0 means, on average, the driver finishes "
        "3 places ahead of their grid slot. The \"Min races\" filter removes one-off flukes "
        "by requiring a minimum sample size."
        '</p>',
        unsafe_allow_html=True,
    )
    ov_c1, ov_c2, ov_c3, ov_c4 = st.columns(4)
    with ov_c1:
        ov_range = st.slider(
            "Seasons", min_value=global_start_year, max_value=global_end_year,
            value=(max(global_start_year, global_end_year - 10), global_end_year),
            key="ov_range",
        )
    with ov_c2:
        ov_min_races = st.slider("Min races", 3, 30, 8, key="ov_min")
    with ov_c3:
        ov_top_n = st.slider("Top N drivers", 5, 25, 12, key="ov_top")
    with ov_c4:
        ov_constructors = st.multiselect(
            "Constructor filter", options=constructor_options, default=[], key="ov_con",
        )

    ov_circuits = st.multiselect(
        "Circuit filter", options=circuit_options, default=[], key="ov_cir",
    )

    overperformer_df = cached_overperformers(
        ov_range[0], ov_range[1],
        tuple(ov_constructors), tuple(ov_circuits),
        ov_min_races, ov_top_n,
    )
    if overperformer_df.empty:
        st.info("No overperformer data for selected filters.")
    else:
        ov_chart = (
            alt.Chart(overperformer_df)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X("avg_finish_gain:Q", title="Avg Positions Gained (Quali -> Finish)"),
                y=alt.Y("driver_full_name:N", sort="-x", title=""),
                color=alt.Color(
                    "gain_races:Q",
                    title="Races with Gain",
                    scale=alt.Scale(scheme="oranges"),
                ),
                tooltip=[
                    "driver_full_name",
                    "races_with_quali_data",
                    alt.Tooltip("avg_finish_gain:Q", format=".2f"),
                    "gain_races",
                ],
            )
            .properties(height=380)
        )
        st.altair_chart(polish_chart(ov_chart), use_container_width=True)

    st.divider()

    # Pit stop scatter
    st.markdown('<div class="section-header">Pit Stop Time vs Finish Gain</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-desc">'
        "Does faster pit work translate into better race results? Each dot represents one "
        "driver in one race. The X-axis shows cumulative pit stop time; the Y-axis shows "
        "<b>adjusted finish gain</b> — how many positions the driver gained relative to their "
        "qualifying slot (positive = finished ahead of grid position). "
        "Look for clusters in the upper-left: drivers with quick pit stops who also gained positions."
        '</p>',
        unsafe_allow_html=True,
    )
    pit_c1, pit_c2, pit_c3 = st.columns(3)
    with pit_c1:
        pit_range = st.slider(
            "Seasons", min_value=global_start_year, max_value=global_end_year,
            value=(max(global_start_year, global_end_year - 10), global_end_year),
            key="pit_range",
        )
    with pit_c2:
        pit_constructors = st.multiselect(
            "Constructor filter", options=constructor_options, default=[], key="pit_con",
        )
    with pit_c3:
        pit_circuits = st.multiselect(
            "Circuit filter", options=circuit_options, default=[], key="pit_cir",
        )

    pitstop_df = cached_pitstop_impact(
        pit_range[0], pit_range[1],
        tuple(pit_constructors), tuple(pit_circuits),
    )
    if pitstop_df.empty:
        st.info("No pit stop data for selected filters.")
    else:
        pit_chart = (
            alt.Chart(pitstop_df)
            .mark_circle(size=70, opacity=0.6)
            .encode(
                x=alt.X("total_pit_stop_ms:Q", title="Total Pit Stop Time (ms)"),
                y=alt.Y("adjusted_finish_gain:Q", title="Adjusted Finish Gain"),
                color=alt.Color("constructor_name:N", title="Constructor"),
                tooltip=[
                    "season_year", "race_name", "circuit_name",
                    "driver_full_name", "constructor_name",
                    "pit_stop_count",
                    alt.Tooltip("total_pit_stop_ms:Q", format=",.0f"),
                    alt.Tooltip("adjusted_finish_gain:Q", format=".1f"),
                    "points",
                ],
            )
            .properties(height=400)
            .interactive()
        )
        st.altair_chart(polish_chart(pit_chart), use_container_width=True)


# ── Tab 3: Season Standings ───────────────────────────────────────────────
with tab_standings:
    st.markdown(
        '<p class="section-desc">'
        "Final championship standings at the end of a selected season. "
        "The charts show the top finishers ranked by total points, with full "
        "standings (including wins and podiums) available in the expandable table below."
        '</p>',
        unsafe_allow_html=True,
    )

    s_c1, s_c2 = st.columns(2)
    with s_c1:
        standings_season = st.selectbox(
            "Season",
            options=list(range(global_end_year, global_start_year - 1, -1)),
            key="standings_season",
        )
    with s_c2:
        standings_top_n = st.slider("Top N", 5, 30, 20, key="standings_top_n")

    driver_pts_df = cached_driver_final_points(standings_season, standings_top_n)
    constructor_pts_df = cached_constructor_final_points(standings_season, standings_top_n)

    # Charts
    chart_c1, chart_c2 = st.columns(2)
    with chart_c1:
        st.markdown('<div class="section-header">Driver Championship</div>', unsafe_allow_html=True)
        if driver_pts_df.empty:
            st.info("No driver standings data.")
        else:
            d_chart = (
                alt.Chart(driver_pts_df.head(15))
                .mark_bar(cornerRadiusEnd=4)
                .encode(
                    x=alt.X("total_points:Q", title="Points"),
                    y=alt.Y("driver_full_name:N", sort="-x", title=""),
                    color=alt.Color(
                        "total_points:Q",
                        scale=alt.Scale(scheme="reds"),
                        legend=None,
                    ),
                    tooltip=["driver_full_name", "total_points", "wins", "podiums"],
                )
                .properties(height=340)
            )
            st.altair_chart(polish_chart(d_chart), use_container_width=True)

    with chart_c2:
        st.markdown('<div class="section-header">Constructor Championship</div>', unsafe_allow_html=True)
        if constructor_pts_df.empty:
            st.info("No constructor standings data.")
        else:
            c_chart = (
                alt.Chart(constructor_pts_df.head(15))
                .mark_bar(cornerRadiusEnd=4)
                .encode(
                    x=alt.X("total_points:Q", title="Points"),
                    y=alt.Y("constructor_name:N", sort="-x", title=""),
                    color=alt.Color(
                        "total_points:Q",
                        scale=alt.Scale(scheme="blues"),
                        legend=None,
                    ),
                    tooltip=["constructor_name", "total_points", "wins", "podiums"],
                )
                .properties(height=340)
            )
            st.altair_chart(polish_chart(c_chart), use_container_width=True)

    # Full tables underneath
    with st.expander("Full standings tables", expanded=False):
        t_c1, t_c2 = st.columns(2)
        with t_c1:
            st.markdown("**Driver Standings**")
            st.dataframe(driver_pts_df, use_container_width=True, hide_index=True)
        with t_c2:
            st.markdown("**Constructor Standings**")
            st.dataframe(constructor_pts_df, use_container_width=True, hide_index=True)


# ── Tab 4: Circuits & History ─────────────────────────────────────────────
with tab_tracks:
    st.markdown(
        '<p class="section-desc">'
        "Pick a circuit to see every race winner in the selected season range. "
        "The donut chart shows which constructors have won the most at that track — "
        "useful for spotting circuit-specific dominance (e.g. Mercedes at Silverstone)."
        '</p>',
        unsafe_allow_html=True,
    )

    tr_c1, tr_c2 = st.columns([1, 2])
    with tr_c1:
        track_range = st.slider(
            "Season range",
            min_value=global_start_year,
            max_value=global_end_year,
            value=(global_start_year, global_end_year),
            key="track_range",
        )
        selected_circuit = st.selectbox(
            "Circuit",
            options=circuit_options if circuit_options else ["No circuits available"],
            key="track_circuit",
        )

    if circuit_options:
        track_df = cached_track_historic(track_range[0], track_range[1], selected_circuit)
        if track_df.empty:
            st.info("No data for this circuit and season range.")
        else:
            with tr_c2:
                # Win count by constructor at this circuit
                wins_by_team = (
                    track_df.groupby("winner_constructor", as_index=False)
                    .size()
                    .rename(columns={"size": "wins"})
                    .sort_values("wins", ascending=False)
                )
                dom_chart = (
                    alt.Chart(wins_by_team)
                    .mark_arc(innerRadius=55, outerRadius=120, stroke="#fff", strokeWidth=2)
                    .encode(
                        theta=alt.Theta("wins:Q", stack=True),
                        color=alt.Color(
                            "winner_constructor:N",
                            title="Constructor",
                            scale=alt.Scale(range=F1_PALETTE),
                            sort=alt.EncodingSortField("wins", order="descending"),
                        ),
                        tooltip=["winner_constructor", "wins"],
                    )
                    .properties(height=300, title=f"Constructor Dominance — {selected_circuit}")
                )
                st.altair_chart(polish_chart(dom_chart), use_container_width=True)

            st.markdown('<div class="section-header">Race-by-Race Winners</div>', unsafe_allow_html=True)
            st.dataframe(
                track_df.rename(columns={
                    "season_year": "Year",
                    "race_name": "Race",
                    "circuit_name": "Circuit",
                    "winner_driver": "Winner",
                    "winner_constructor": "Constructor",
                    "winner_points": "Points",
                }),
                use_container_width=True,
                hide_index=True,
            )


# ── Tab 5: Race Explorer ─────────────────────────────────────────────────
with tab_races:
    st.markdown(
        '<p class="section-desc">'
        "Select a season and race to inspect the full results grid. "
        "The slope chart shows how each driver's position changed from the starting grid "
        "to the final finish — lines going up (toward P1) indicate positions gained, "
        "lines dropping down show positions lost. The full table includes pit stop data and DNF status."
        '</p>',
        unsafe_allow_html=True,
    )

    rc_c1, rc_c2 = st.columns(2)
    with rc_c1:
        race_season = st.selectbox(
            "Season",
            options=list(range(global_end_year, global_start_year - 1, -1)),
            key="race_season",
        )
    race_opts_df = cached_race_options(race_season)
    if race_opts_df.empty:
        st.info("No races found for this season.")
    else:
        race_labels = race_opts_df["race_label"].tolist()
        race_lookup = dict(zip(race_labels, race_opts_df["race_id"].tolist()))
        with rc_c2:
            selected_race = st.selectbox("Race", options=race_labels, key="race_label")

        detail_df = cached_race_detail(int(race_lookup[selected_race]))

        if not detail_df.empty:
            # Grid vs Finish position chart for top finishers
            chart_df = detail_df.copy()
            chart_df = chart_df.dropna(subset=["grid", "finish_position"])
            chart_df = chart_df[chart_df["finish_position"] <= 20]

            if not chart_df.empty:
                melt_df = chart_df.melt(
                    id_vars=["driver_full_name"],
                    value_vars=["grid", "finish_position"],
                    var_name="stage",
                    value_name="position",
                )
                melt_df["stage"] = melt_df["stage"].map(
                    {"grid": "Grid", "finish_position": "Finish"}
                )
                slope_chart = (
                    alt.Chart(melt_df)
                    .mark_line(point=True, strokeWidth=2)
                    .encode(
                        x=alt.X("stage:N", title="", sort=["Grid", "Finish"],
                                axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("position:Q", title="Position",
                                scale=alt.Scale(reverse=True)),
                        color=alt.Color("driver_full_name:N", title="Driver"),
                        tooltip=["driver_full_name", "stage", "position"],
                    )
                    .properties(height=380, title="Grid vs Finish Position")
                    .interactive()
                )
                st.altair_chart(polish_chart(slope_chart), use_container_width=True)

            with st.expander("Full race results", expanded=True):
                st.dataframe(
                    detail_df.rename(columns={
                        "driver_full_name": "Driver",
                        "constructor_name": "Constructor",
                        "grid": "Grid",
                        "finish_position": "Finish",
                        "points": "Points",
                        "finish_position_delta": "Delta",
                        "pit_stop_count": "Pit Stops",
                        "total_pit_stop_ms": "Pit Time (ms)",
                        "status_description": "Status",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )

st.markdown(
    f'<div class="footer-bar">'
    f'F1 Race Analytics &mdash; Seasons {global_start_year}&ndash;{global_end_year} '
    f'&middot; Live queries against <b>Neon PostgreSQL</b>, transformed by <b>dbt</b> '
    f'&middot; Deployed on <b>Render</b> &middot; '
    f'Built for EAS 550 &mdash; DMQL'
    f'</div>',
    unsafe_allow_html=True,
)
