import streamlit as st
import pandas as pd
import logging
import swc_simple_client as swc
import nfl_data_py as nfl
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

st.header("SportsWorldCentral Data App")
st.subheader("Team Stats and Trends")

base_url = st.session_state['base_url']

try:
    # Cached API calls for faster navigation and reruns.
    teams_data = swc.get_api_json_cached(base_url, swc.LIST_TEAMS_ENDPOINT)
    
    teams_df = pd.DataFrame(teams_data)

    unique_leagues = sorted(teams_df['league_id'].astype(str).unique())
    selected_league = st.sidebar.selectbox('Pick league ID', unique_leagues)

    st.sidebar.divider()
    st.sidebar.subheader(":blue[Data sources]")
    st.sidebar.text("SportWorldCentral")
    st.sidebar.text("NFLDataPy")

    flat_team_df = pd.json_normalize(teams_data, 'players', ['team_id', 'team_name', 'league_id'])
    flat_team_df['league_id'] = flat_team_df['league_id'].astype(str)
    league_roster_df = flat_team_df[flat_team_df['league_id'] == selected_league].copy()

    st.markdown("### Visualization 1: Player Position Mix")
    position_df = (
        league_roster_df.groupby('position', as_index=False)
        .size()
        .rename(columns={'size': 'player_count'})
        .sort_values('player_count', ascending=False)
    )
    st.bar_chart(position_df, x='position', y='player_count')

    st.markdown("### Visualization 2: Total Touchdowns by Team (2023)")
    nfl_data_2023_df = nfl.import_seasonal_data([2023], "REG")
    nfl_data_2023_subset_df = nfl_data_2023_df[
        ["player_id", "passing_tds", "rushing_tds", "receiving_tds"]
    ].copy()
    nfl_data_2023_subset_df["total_tds"] = (
        nfl_data_2023_subset_df["passing_tds"]
        + nfl_data_2023_subset_df["rushing_tds"]
        + nfl_data_2023_subset_df["receiving_tds"]
    )

    merged_df = pd.merge(
        league_roster_df,
        nfl_data_2023_subset_df,
        how="left",
        left_on="gsis_id",
        right_on="player_id",
    )

    team_tds_df = merged_df.groupby("team_name")["total_tds"].sum().reset_index()
    team_tds_df["total_tds"] = team_tds_df["total_tds"].fillna(0)
    team_tds_df = team_tds_df.sort_values(by="total_tds", ascending=False)

    st.line_chart(team_tds_df.set_index("team_name")["total_tds"])

    st.markdown("### Visualization 3: Top Players by Total Touchdowns (2023)")
    player_tds_df = (
        merged_df.groupby(["first_name", "last_name"], as_index=False)["total_tds"]
        .sum()
        .fillna(0)
        .sort_values(by="total_tds", ascending=False)
        .head(10)
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(
        player_tds_df["first_name"] + " " + player_tds_df["last_name"],
        player_tds_df["total_tds"],
    )
    ax.set_xlabel("Total TDs")
    ax.set_ylabel("Player")
    ax.set_title("Top 10 Players by Total TDs - 2023")
    st.pyplot(fig)

    st.caption(f"Showing {len(league_roster_df)} players across league {selected_league}.")
    
except Exception as e:
    logger.error(f"Exception encountered on Team Stats page: {str(e)}")
    st.write(f"An unexpected error occurred: {str(e)}") # catch any unhandled exceptions and display an error message on the page
    