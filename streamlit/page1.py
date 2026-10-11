import logging

import httpx
import pandas as pd
import streamlit as st

import swc_simple_client as swc

logger = logging.getLogger(__name__)

st.header("SportWorldCentral Data App")
st.subheader("Team Rosters Page")

base_url = st.session_state.get('base_url')

# Validate session state
if not base_url:
    st.error("Base URL not configured. Please restart the app.")
    st.stop()

try:
    # Load teams data with caching
    team_data = swc.get_api_json_cached(base_url, swc.LIST_TEAMS_ENDPOINT)
    teams_df = pd.DataFrame(team_data)
    
    # Get unique leagues from teams data
    unique_leagues = sorted(teams_df['league_id'].unique().astype(str))
    
    # Store the unique leagues in the session state
    st.session_state['unique_leagues'] = unique_leagues
    
    st.sidebar.divider()
    st.sidebar.subheader(":blue[Data sources]")
    st.sidebar.text("SportWorldCentral")

    # Flatten the team data so each row represents a player
    flat_team_df = pd.json_normalize(
        team_data, 
        'players', 
        ['team_id', 'team_name', 'league_id']
    )
    
    column_order = [
        'league_id', 'team_id', 'team_name', 'position',
        'player_id', 'gsis_id', 'first_name', 'last_name'
    ]
    flat_team_df_ordered = flat_team_df[column_order]
    st.session_state['flat_team_df_ordered'] = flat_team_df_ordered
    
    # Create dropdown for league selection
    selected_league = st.sidebar.selectbox('Pick league ID', unique_leagues)
    
    # Filter by selected league
    display_df = flat_team_df_ordered.copy()
    display_df['league_id'] = display_df['league_id'].astype(str)
    display_df = display_df[display_df['league_id'] == selected_league]
    
    # Drop internal IDs from display
    display_df = display_df.drop(columns=['team_id', 'player_id'])
    
    st.dataframe(display_df, hide_index=True)

except httpx.HTTPStatusError as e:
    logger.exception("API returned HTTP %s while loading team data", e.response.status_code)
    st.error(
        f"The API returned HTTP {e.response.status_code} while loading team data. "
        "The backend is reachable, but its team-data endpoint is currently failing."
    )
    st.caption(f"API: {base_url}")
except httpx.RequestError:
    logger.exception("Could not connect to the API while loading team data")
    st.error("Could not connect to the API while loading team data.")
    st.caption(f"API: {base_url}")
except RuntimeError as e:
    logger.error(f"API error: {str(e)}")
    st.error("Failed to load team data. Please try again later.")
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    st.caption("Data is temporarily unavailable.")
