from dotenv import load_dotenv

import logging
import os

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

# Load the variables from the .env file
load_dotenv()

DEFAULT_API_BASE_URL = "https://fantasyfootball-api-service-lmm2.onrender.com"


def init_session_state() -> None:
    """Initialize session state variables with proper defaults and URL validation."""
    try:
        secrets_base_url = st.secrets.get("API_BASE_URL")
    except StreamlitSecretNotFoundError:
        secrets_base_url = None

    default_base_url = (
        os.getenv("API_BASE_URL") or secrets_base_url or DEFAULT_API_BASE_URL
    )
    
    # Initialize base_url if not set or empty
    if 'base_url' not in st.session_state or not st.session_state.get('base_url'):
        st.session_state['base_url'] = default_base_url.strip().rstrip("/")
    
    # Ensure the URL has a scheme so httpx can build valid request URLs.
    base_url = st.session_state.get('base_url', default_base_url)
    if not base_url.startswith(("http://", "https://")):
        st.session_state['base_url'] = f"http://{base_url}"


def configure_logging() -> None:
    """Configure application logging with a consistent format."""
    logging.basicConfig(
        filename='football_app.log',
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


# Initialize session state and logging
init_session_state()
configure_logging()

# set the configuration for the Streamlit app
st.set_page_config(page_title="Football App",
                   page_icon=":material/sports_football:") 

page_1 = st.Page("page1.py", title="Team Rosters", icon=":material/trophy:")
page_2 = st.Page("page2.py", title="Team Stats", icon=":material/star_border:")

# create a navigation menu for the app
pg = st.navigation([page_1, page_2])
pg.run() # run the Streamlit app
