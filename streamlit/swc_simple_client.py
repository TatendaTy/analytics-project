import backoff
import logging
import httpx
import streamlit as st

HEALTH_CHECK_ENDPOINT = "/"
LIST_LEAGUES_ENDPOINT = "/v0/leagues/"
LIST_PLAYERS_ENDPOINT = "/v0/players/"
LIST_PERFORMANCES_ENDPOINT = "/v0/performances/"
LIST_TEAMS_ENDPOINT = "/v0/teams/"
LIST_WEEKS_ENDPOINT = "/v0/weeks/"
GET_COUNTS_ENDPOINT = "/v0/counts/"

logger = logging.getLogger(__name__) # get reference to the log file

@backoff.on_exception(
    wait_gen=backoff.expo,
    exception=(httpx.RequestError, httpx.HTTPStatusError),
    max_time=5,
    jitter=backoff.random_jitter
)
def call_api_endpoint(
    base_url: str,
    api_endpoint: str,
    api_params: dict = None
) -> httpx.Response:
    try:
        # make API call and then clean resources when done
        with httpx.Client(base_url=base_url) as client:
            logger.debug(f"base url: {base_url}, api_endpoint: {api_endpoint})")
            response = client.get(api_endpoint, params=api_params)
            response.raise_for_status()
            logger.debug(f"Response JSON: {response.json()}") # log the API response for debugging
            return response
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP status error occured: {e.response.text}")
        return httpx.Response(status_code=e.response.status_code, content=b"API error")
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {str(e)}")
        return httpx.Response(status_code=500, content=b"Network error")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        return httpx.Response(status_code=500, content=b"Unexpected error")


@st.cache_data(ttl=300, show_spinner=False)
def get_api_json_cached(
    base_url: str,
    api_endpoint: str,
    api_params_items: tuple = None,
) -> list[dict]:
    """Fetch endpoint JSON and cache the result for faster reruns.

    api_params_items is a hashable tuple of key/value pairs so the function
    can be safely cached by Streamlit.
    """
    api_params = dict(api_params_items) if api_params_items else None
    response = call_api_endpoint(base_url, api_endpoint, api_params)
    if response.status_code != 200:
        raise RuntimeError(f"API call failed: {response.status_code} {response.text}")
    return response.json()