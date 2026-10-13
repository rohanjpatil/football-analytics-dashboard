import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

POSITION_COLORS = {
    "GK": "#1E90FF",
    "DEF": "#FFD700",
    "MID": "#00C853",
    "FWD": "#FF4500",
}

REQUIRED_COLUMNS = [
    "player_id", "player_name", "team", "position", "season",
    "age", "matches_played", "minutes_played", "goals", "assists",
    "shots", "shots_on_target", "passes", "pass_accuracy", "tackles",
    "yellow_cards", "red_cards", "rating", "data_source",
]


def inject_css():
    st.markdown(
        """
        <style>
        .kpi-card {
            background: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 16px 20px;
            text-align: center;
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            color: #00C853;
        }
        .kpi-label {
            font-size: 0.85rem;
            color: #8B949E;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data():
    df = pd.read_csv("football_players.csv", encoding="utf-8")
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()
    return df


def render_sidebar(df):
    st.sidebar.title("⚽ Football Analytics")
    st.sidebar.caption("Performance Dashboard")
    st.sidebar.divider()

    all_seasons = sorted(df["season"].unique().tolist())
    seasons = st.sidebar.multiselect(
        "Season",
        options=all_seasons,
        default=all_seasons,
    )

    all_teams = sorted(df["team"].unique().tolist())
    teams = st.sidebar.multiselect(
        "Team",
        options=all_teams,
        default=all_teams,
    )

    all_positions = ["GK", "DEF", "MID", "FWD"]
    positions = st.sidebar.multiselect(
        "Position",
        options=all_positions,
        default=all_positions,
    )

    # Dynamically filter player list based on the above selections
    mask = pd.Series([True] * len(df), index=df.index)
    if seasons:
        mask &= df["season"].isin(seasons)
    if teams:
        mask &= df["team"].isin(teams)
    if positions:
        mask &= df["position"].isin(positions)
    all_players = sorted(df.loc[mask, "player_name"].unique().tolist())

    players = st.sidebar.multiselect(
        "Player",
        options=all_players,
        default=all_players,
    )

    return seasons, teams, positions, players


def apply_filters(df, seasons, teams, positions, players):
    filtered = df.copy()
    if seasons:
        filtered = filtered[filtered["season"].isin(seasons)]
    if teams:
        filtered = filtered[filtered["team"].isin(teams)]
    if positions:
        filtered = filtered[filtered["position"].isin(positions)]
    if players:
        filtered = filtered[filtered["player_name"].isin(players)]
    return filtered


def render_overview_page(filtered_df, full_df):
    # --- Section 1: KPI Row ---
    full_players = len(full_df["player_id"].unique())
    full_goals = full_df["goals"].sum()
    full_assists = full_df["assists"].sum()
    full_minutes = full_df["minutes_played"].sum()
    full_rating = round(full_df["rating"].mean(), 2)

    filtered_players = len(filtered_df["player_id"].unique())
    filtered_goals = filtered_df["goals"].sum()
    filtered_assists = filtered_df["assists"].sum()
    filtered_minutes = filtered_df["minutes_played"].sum()
    filtered_rating = round(filtered_df["rating"].mean(), 2)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(
        "Total Players",
        int(filtered_players),
        delta=int(filtered_players - full_players),
    )
    col2.metric(
        "Total Goals",
        int(filtered_goals),
        delta=int(filtered_goals - full_goals),
    )
    col3.metric(
        "Total Assists",
        int(filtered_assists),
        delta=int(filtered_assists - full_assists),
    )
    col4.metric(
        "Total Minutes",
        f"{filtered_minutes:,}",
        delta=int(filtered_minutes - full_minutes),
    )
    col5.metric(
        "Avg Rating",
        float(filtered_rating),
        delta=round(float(filtered_rating - full_rating), 2),
    )

    st.divider()

    # --- Section 2: Top Players Leaderboard ---
    st.subheader("🏆 Top Players Leaderboard")

    sort_label = st.selectbox(
        "Sort by",
        ["Rating", "Goals", "Assists", "Minutes Played"],
    )
    sort_col_map = {
        "Rating": "rating",
        "Goals": "goals",
        "Assists": "assists",
        "Minutes Played": "minutes_played",
    }
    sort_col = sort_col_map[sort_label]

    display_cols = [
        "player_name", "team", "position", "season",
        "goals", "assists", "rating", "minutes_played",
    ]
    top10 = (
        filtered_df[display_cols]
        .sort_values(sort_col, ascending=False)
        .head(10)
    )
    st.dataframe(top10, use_container_width=True, hide_index=True)

    st.divider()

    # --- Section 3: Synthetic data notice ---
    st.info(
        "ℹ️ All statistics are synthetic and generated for demonstration purposes only. "
        "They do not represent real football data."
    )

    st.divider()

    # --- Section 4: Player Statistics ---
    st.subheader("📋 Player Statistics")

    search = st.text_input("🔍 Search player by name", placeholder="e.g. Marco Silva")

    table_df = filtered_df.copy()
    if search:
        table_df = table_df[table_df['player_name'].str.contains(search, case=False, na=False)]

    st.caption(f"Showing {len(table_df):,} of {len(filtered_df):,} players")

    display_cols = ['player_name', 'team', 'position', 'season', 'age', 'matches_played',
                    'minutes_played', 'goals', 'assists', 'shots', 'shots_on_target',
                    'passes', 'pass_accuracy', 'tackles', 'yellow_cards', 'red_cards', 'rating']
    st.dataframe(table_df[display_cols], use_container_width=True, hide_index=True)

    csv_bytes = table_df[display_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name="football_stats_filtered.csv",
        mime="text/csv",
    )


def render_player_page(filtered_df):
    # --- Section 1: Player Comparison ---
    st.subheader("🔍 Player Comparison")

    player_names = sorted(filtered_df["player_name"].unique().tolist())

    if len(player_names) < 2:
        st.warning("Select at least 2 players to compare.")
    else:
        col_left, col_right = st.columns(2)
        with col_left:
            player1 = st.selectbox("Player 1", options=player_names, index=0)
        with col_right:
            player2 = st.selectbox("Player 2", options=player_names, index=1)

        stat_cols = [
            "age", "team", "position", "season", "matches_played",
            "minutes_played", "goals", "assists", "shots", "shots_on_target",
            "pass_accuracy", "tackles", "yellow_cards", "rating",
        ]

        def _latest_row(name):
            rows = filtered_df[filtered_df["player_name"] == name].sort_values(
                "season", ascending=False
            )
            return rows.iloc[0][stat_cols]

        row1 = _latest_row(player1)
        row2 = _latest_row(player2)

        comparison_df = pd.DataFrame(
            {player1: row1, player2: row2},
            index=stat_cols,
        )
        st.dataframe(comparison_df, use_container_width=True)

    st.divider()

    # --- Section 2: Scatter charts ---
    col_a, col_b = st.columns(2)

    with col_a:
        fig_ga = px.scatter(
            filtered_df,
            x="assists",
            y="goals",
            color="position",
            size="rating",
            hover_name="player_name",
            hover_data=["team", "season", "rating"],
            title="Goals vs Assists",
            template="plotly_dark",
            color_discrete_map=POSITION_COLORS,
        )
        fig_ga.update_layout(xaxis_title="Assists", yaxis_title="Goals")
        st.plotly_chart(fig_ga, use_container_width=True)
        st.caption("Bubble size = player rating. Colour = position.")

    with col_b:
        max_shots = int(filtered_df["shots"].max()) if not filtered_df.empty else 1
        fig_sg = px.scatter(
            filtered_df,
            x="shots",
            y="goals",
            color="position",
            size="rating",
            hover_name="player_name",
            hover_data=["team", "season", "shots_on_target"],
            title="Shots vs Goals (Conversion Efficiency)",
            template="plotly_dark",
            color_discrete_map=POSITION_COLORS,
        )
        fig_sg.add_trace(
            go.Scatter(
                x=[0, max_shots],
                y=[0, max_shots],
                mode="lines",
                line=dict(color="#8B949E", dash="dash"),
                name="Perfect Conversion",
                showlegend=True,
            )
        )
        fig_sg.update_layout(xaxis_title="Shots", yaxis_title="Goals")
        st.plotly_chart(fig_sg, use_container_width=True)
        st.caption("Dashed line = 100% conversion rate (reference only).")


def render_team_page(filtered_df):
    # --- Aggregation ---
    team_df = (
        filtered_df.groupby("team")
        .agg(
            total_goals=("goals", "sum"),
            total_assists=("assists", "sum"),
            player_count=("player_id", "nunique"),
            avg_rating=("rating", "mean"),
            total_minutes=("minutes_played", "sum"),
        )
        .reset_index()
        .sort_values("total_goals", ascending=False)
    )
    team_df["avg_rating"] = team_df["avg_rating"].round(2)

    # --- Chart 1: Grouped Goals & Assists Bar Chart (full width) ---
    st.subheader("⚽ Goals & Assists by Team")
    fig_ga = go.Figure()
    fig_ga.add_trace(
        go.Bar(
            x=team_df["team"],
            y=team_df["total_goals"],
            name="Goals",
            marker_color="#00C853",
        )
    )
    fig_ga.add_trace(
        go.Bar(
            x=team_df["team"],
            y=team_df["total_assists"],
            name="Assists",
            marker_color="#1E90FF",
        )
    )
    fig_ga.update_layout(
        barmode="group",
        template="plotly_dark",
        xaxis_title="Team",
        yaxis_title="Count",
        legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig_ga, use_container_width=True)

    # --- Charts 2 & 3: Side by side ---
    col_left, col_right = st.columns(2)

    with col_left:
        team_df_sorted = team_df.sort_values("avg_rating", ascending=True)
        fig_rating = px.bar(
            team_df_sorted,
            x="avg_rating",
            y="team",
            orientation="h",
            title="Average Player Rating by Team",
            template="plotly_dark",
            color="avg_rating",
            color_continuous_scale=["#1E3A5F", "#00C853"],
            labels={"avg_rating": "Avg Rating", "team": "Team"},
        )
        fig_rating.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_rating, use_container_width=True)

    with col_right:
        fig_count = px.bar(
            team_df,
            x="team",
            y="player_count",
            title="Player Count by Team",
            template="plotly_dark",
            color="player_count",
            color_continuous_scale=["#1E3A5F", "#FFD700"],
            labels={"player_count": "Players", "team": "Team"},
        )
        fig_count.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_count, use_container_width=True)

    # --- Summary Table ---
    st.subheader("📊 Team Summary")
    st.dataframe(
        team_df.rename(
            columns={
                "team": "Team",
                "total_goals": "Goals",
                "total_assists": "Assists",
                "player_count": "Players",
                "avg_rating": "Avg Rating",
                "total_minutes": "Total Minutes",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_position_page(filtered_df):
    st.subheader("Position Analysis")

    def minmax(series):
        mn, mx = series.min(), series.max()
        if mx == mn:
            return series * 0
        return (series - mn) / (mx - mn)

    labels = ["GK", "DEF", "MID", "FWD"]

    # ── Row 1 ──────────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    # Left — Donut chart: player count by position
    with col1:
        values = [len(filtered_df[filtered_df["position"] == p]) for p in labels]
        fig_donut = go.Figure(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(colors=[POSITION_COLORS[p] for p in labels]),
            )
        )
        fig_donut.update_layout(
            title="Player Distribution by Position",
            template="plotly_dark",
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # Right — Radar chart: average stats per position
    with col2:
        metrics = ["goals", "assists", "pass_accuracy", "tackles", "rating"]

        # Per-position averages → DataFrame (rows=positions, cols=metrics)
        avg_df = (
            filtered_df[filtered_df["position"].isin(labels)]
            .groupby("position")[metrics]
            .mean()
            .reindex(labels)
            .fillna(0)
        )

        # Normalise each metric column across positions
        norm_df = avg_df.apply(minmax, axis=0)

        fig_radar = go.Figure()
        for pos in labels:
            r_vals = norm_df.loc[pos].tolist()
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=r_vals + [r_vals[0]],
                    theta=metrics + [metrics[0]],
                    mode="lines+markers",
                    fill="toself",
                    name=pos,
                    line=dict(color=POSITION_COLORS[pos]),
                    marker=dict(color=POSITION_COLORS[pos]),
                )
            )
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            template="plotly_dark",
            title="Position Attributes Radar",
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── Row 2 ──────────────────────────────────────────────────────────────────
    col3, col4 = st.columns(2)

    # Left — Box plot: goals distribution by position
    with col3:
        fig_goals = px.box(
            filtered_df,
            x="position",
            y="goals",
            color="position",
            title="Goals Distribution by Position",
            template="plotly_dark",
            color_discrete_map=POSITION_COLORS,
            category_orders={"position": labels},
        )
        fig_goals.update_layout(showlegend=False)
        st.plotly_chart(fig_goals, use_container_width=True)

    # Right — Box plot: assists distribution by position
    with col4:
        fig_assists = px.box(
            filtered_df,
            x="position",
            y="assists",
            color="position",
            title="Assists Distribution by Position",
            template="plotly_dark",
            color_discrete_map=POSITION_COLORS,
            category_orders={"position": labels},
        )
        fig_assists.update_layout(showlegend=False)
        st.plotly_chart(fig_assists, use_container_width=True)


def main():
    st.set_page_config(
        page_title="⚽ Football Analytics",
        layout="wide",
        page_icon="⚽",
    )

    inject_css()

    df = load_data()

    seasons, teams, positions, players = render_sidebar(df)

    filtered_df = apply_filters(df, seasons, teams, positions, players)

    if filtered_df.empty:
        st.warning("No data matches the current filters.")
        st.stop()

    page = st.sidebar.radio(
        "Navigation",
        ["Overview", "Player Analysis", "Team Analysis", "Position Analysis"],
    )

    if page == "Overview":
        render_overview_page(filtered_df, df)
    elif page == "Player Analysis":
        render_player_page(filtered_df)
    elif page == "Team Analysis":
        render_team_page(filtered_df)
    elif page == "Position Analysis":
        render_position_page(filtered_df)

    st.sidebar.caption(
        "⚠️ All data is synthetic and does not represent real football statistics."
    )


if __name__ == "__main__":
    main()
