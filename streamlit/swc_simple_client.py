import logging
from typing import Any

import backoff
import httpx
import streamlit as st

logger = logging.getLogger(__name__)

HEALTH_CHECK_ENDPOINT = "/"
LIST_LEAGUES_ENDPOINT = "/v0/leagues/"
LIST_PLAYERS_ENDPOINT = "/v0/players/"
LIST_PERFORMANCES_ENDPOINT = "/v0/performances/"
LIST_TEAMS_ENDPOINT = "/v0/teams/"
LIST_WEEKS_ENDPOINT = "/v0/weeks/"
GET_COUNTS_ENDPOINT = "/v0/counts/"


@backoff.on_exception(
    wait_gen=backoff.expo,
    exception=(httpx.RequestError, httpx.HTTPStatusError),
    max_time=5,
    jitter=backoff.random_jitter
)
def call_api_endpoint(
    base_url: str,
    api_endpoint: str,
    api_params: dict[str, Any] | None = None
) -> httpx.Response:
    """Make an HTTP GET request to the API endpoint with retry logic."""
    logger.debug(f"Calling: base_url={base_url}, endpoint={api_endpoint}")
    
    with httpx.Client(base_url=base_url) as client:
        response = client.get(api_endpoint, params=api_params)
        response.raise_for_status()
        logger.debug(f"Response: {response.json()}")
        return response


@st.cache_data(ttl=300, show_spinner=False)
def get_api_json_cached(
    base_url: str,
    api_endpoint: str,
    api_params_items: tuple[tuple[str, Any], ...] | None = None,
) -> list[dict[str, Any]]:
    """Fetch endpoint JSON and cache the result for faster reruns.
    
    Args:
        base_url: The base URL of the API.
        api_endpoint: The API endpoint path.
        api_params_items: Optional hashable tuple of key/value pairs for caching.
    
    Returns:
        List of dictionaries from the API response JSON.
    
    Raises:
        RuntimeError: If the API call fails.
    """
    api_params = dict(api_params_items) if api_params_items else None
    response = call_api_endpoint(base_url, api_endpoint, api_params)
    return response.json()