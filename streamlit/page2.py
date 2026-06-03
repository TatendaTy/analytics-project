import logging

import matplotlib.pyplot as plt
import nfl_data_py as nfl
import pandas as pd
import streamlit as st

import swc_simple_client as swc

logger = logging.getLogger(__name__)

st.header("SportsWorldCentral Data App")
st.subheader("Team Touchdown Totals")

# Check required session state
if 'flat_team_df_ordered' not in st.session_state:
    st.warning("Please visit the Team Rosters page first to load the data.")
    st.stop()

if 'unique_leagues' not in st.session_state:
    st.warning("League data not available. Please restart from the Team Rosters page.")
    st.stop()

flat_team_df_ordered = st.session_state['flat_team_df_ordered']
unique_leagues = st.session_state['unique_leagues']

selected_league = st.sidebar.selectbox('Pick league ID', unique_leagues)

st.sidebar.divider()
st.sidebar.subheader(":blue[Data sources]")
st.sidebar.text("SportsWorldCentral")
st.sidebar.text("NFLDataPy")

try:
    # Filter by selected league
    filtered_df = flat_team_df_ordered.copy()
    filtered_df['league_id'] = filtered_df['league_id'].astype(str)
    filtered_df = filtered_df[filtered_df['league_id'] == selected_league]
    
    # Import NFL data with caching
    @st.cache_data(ttl=3600, show_spinner="Loading NFL data...")
    def load_nfl_data(seasons: list[int], downtype: str) -> pd.DataFrame:
        return nfl.import_seasonal_data(seasons, downtype)
    
    nfl_data_2023_df = load_nfl_data([2023], 'REG')
    
    columns_to_select = ['player_id', 'passing_tds', 'rushing_tds', 'receiving_tds']
    nfl_data_2023_subset_df = nfl_data_2023_df[columns_to_select].copy()
    
    nfl_data_2023_subset_df['total_tds'] = (
        nfl_data_2023_subset_df['passing_tds'] +
        nfl_data_2023_subset_df['rushing_tds'] +
        nfl_data_2023_subset_df['receiving_tds']
    )
    
    merged_df = pd.merge(
        filtered_df,
        nfl_data_2023_subset_df,
        how='left',
        left_on='gsis_id',
        right_on='player_id'
    )
    
    grouped_df = merged_df.groupby('team_name')['total_tds'].sum()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    grouped_df.plot(
        kind='barh',
        xlabel='Total TDs',
        ylabel='Team Name',
        title='Total Touchdowns - 2023',
        ax=ax
    )
    plt.tight_layout()
    st.pyplot(fig)

except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    st.error("An unexpected error occurred. Please try again later.")