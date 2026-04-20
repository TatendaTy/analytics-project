import streamlit as st
import swc_simple_client as swc
import pandas as pd
import logging

logger = logging.getLogger(__name__) #reference the logging file configured in the entrypoint file

# print headings to the top of the page
st.header("SportWorldCentral Data App")
st.subheader("Team Rosters Page")

base_url = st.session_state['base_url'] # retrieve the base_url var from the session state

# catch any unhandled exceptions and log them to the football_app.log file
try:
    # call the API endpoint AND store the response in a variable
    team_api_response = swc.call_api_endpoint(base_url, swc.LIST_TEAMS_ENDPOINT)
    
    if team_api_response.status_code == 200:
        # proceed to populate the page with the team data
        team_data = team_api_response.json() # convert the API response from JSON to a Python dict
        teams_df = pd.DataFrame.from_dict(team_data) # create a DataFrame from the team data dict
        
        unique_leagues = teams_df['league_id'].unique()
        unique_leagues = sorted(unique_leagues.astype(str))
        
        # store the unique leagues in the session state so that they can be used in other pages of the app
        if 'unique_leagues' not in st.session_state:
            st.session_state['unique_leagues'] = unique_leagues
            
        selected_league = st.sidebar.selectbox('Pick league ID', unique_leagues) # create a dropdown menu in the sidebar to select a league ID
        st.sidebar.divider() # add a divider to the sidebar
        st.sidebar.subheader(":blue[Data sources]")
        st.sidebar.text("SportWorldCentral")
        
        # flatten the team data so that each row represents a player, and the team and league information is included in each row
        flat_team_df = pd.json_normalize(team_data, 'players', ['team_id', 'team_name', 'league_id'])
        column_order = ['league_id', 'team_id', 'team_name', 'position',
                        'player_id', 'gsis_id', 'first_name', 'last_name']
        flat_team_df_ordered = flat_team_df[column_order]
        
        if 'flat_team_df_ordered' not in st.session_state:
            st.session_state['flat_team_df_ordered'] = flat_team_df_ordered
        
        display_df = flat_team_df_ordered.drop(columns=['team_id', 'player_id'])
        
        display_df['league_id'] = display_df['league_id'].astype(str)
        display_df = display_df[display_df['league_id'] == selected_league] # filter the DataFrame to only match the values given by the user
        
        st.dataframe(display_df, hide_index=True) # display the team roster data in a table on the page, hiding the index column
    else:
        logger.error(f"Error encountered: {team_api_response.status_code} {team_api_response.text}") # display an error if the API call fails
        st.write("Error encountered while accessing data source.")
        
except Exception as e:
    logger.error(f"Exception encountered: {str(e)}") # log any unhandled exceptions that occur during the execution of the try block
    st.write(f"An unexpected error occured.")