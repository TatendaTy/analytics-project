import streamlit as st
import pandas as pd
import logging
import nfl_data_py as nfl
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

st.header("SportsWorldCentral Data App")
st.subheader("Team Touchdown Totals")

try:
    flat_team_df_ordered = st.session_state['flat_team_df_ordered'] # use the DataFrame stored in the session state by page 1 to access the team and player data
    
    unique_leagues = st.session_state['unique_leagues'] # use the unique leagues stored in the session state by page 1 to populate the dropdown menu for league selection
    selected_league = st.sidebar.selectbox('Pick league ID', unique_leagues)
    
    st.sidebar.divider()
    st.sidebar.subheader(":blue[Data sources]")
    st.sidebar.text("SportWorldCentral")
    st.sidebar.text("NFLDataPy")
    
    flat_team_df_ordered['league_id'] = flat_team_df_ordered['league_id'].astype(str) # filter dataframe to match league_id from the select box in the nav bar
    flat_team_df_ordered = flat_team_df_ordered[flat_team_df_ordered['league_id'] == selected_league]
    
    nfl_data_2023_df = nfl.import_seasonal_data([2023], 'REG') # use nfl_data_py to import play-by-play data for the 2023 regular season
    columns_to_select = ['player_id', 'passing_tds', 'rushing_tds', 'receiving_tds'] # select only the columns needed to calculate total touchdowns for each player
    nfl_data_2023_subset_df = nfl_data_2023_df[columns_to_select].copy()
    
    # create a new column in the play-by-play DataFrame that sums the passing, rushing, and receiving touchdowns for each player to get a total touchdown count for the season
    nfl_data_2023_subset_df['total_tds'] = (
        nfl_data_2023_subset_df['passing_tds'] + 
        nfl_data_2023_subset_df['rushing_tds'] + 
        nfl_data_2023_subset_df['receiving_tds']
    )
    
    # merge the team and player data from the API with the NFL play-by-play data using the gsis_id and player_id columns to match the records for each player
    merged_df = pd.merge(
        flat_team_df_ordered,
        nfl_data_2023_subset_df,
        how='left',
        left_on='gsis_id',
        right_on='player_id'
    )
    
    # group the merged DataFrame by team name and sum the total touchdowns for each team
    grouped_df = merged_df.groupby('team_name')['total_tds'].sum()
    
    # create a horizontal bar chart to visualize the total touchdowns by team for the 2023 season
    fig, ax = plt.subplots()
    grouped_df.plot(kind='barh', xlabel='Total TDs',
                    ylabel="Team Name", title="Total TDs - 2023", ax=ax)
    
    st.pyplot(fig) # display the bar chart on the page
    
except Exception as e:
    st.write(f"An unexpected error occurred: {str(e)}") # catch any unhandled exceptions and display an error message on the page
    