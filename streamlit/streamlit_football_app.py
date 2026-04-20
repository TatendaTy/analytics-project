import streamlit as st
import logging
import pandas as pd

if 'base_url' not in st.session_state:
    st.session_state['base_url'] = "http://127.0.0.1:8000"

# Ensure the URL always has a scheme so httpx can build valid request URLs.
if not st.session_state['base_url'].startswith(("http://", "https://")):
    st.session_state['base_url'] = f"http://{st.session_state['base_url']}"

# configure logging
logging.basicConfig(
    filename='football_app.log',
    level=logging.INFO,
)

# set the configuration for the Streamlit app
st.set_page_config(page_title="Football App",
                   page_icon=":material/sports_football:") 

page_1 = st.Page("page1.py", title="Team Rosters", icon=":material/trophy:")
page_2 = st.Page("page2.py", title="Team Stats", icon=":material/star_border:")

# create a navigation menu for the app
pg = st.navigation([page_1, page_2])
pg.run() # run the Streamlit app

