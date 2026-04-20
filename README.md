# Analytics Portfolio Project

This repository showcases an end-to-end sports analytics engineering workflow built with Python. It combines API design, data modeling, orchestration, and interactive analytics into one portfolio project that is ready to demonstrate on GitHub and a professional portfolio site.

## Project Summary

The project is centered on a fantasy football data domain and demonstrates how raw operational data can move through a complete analytics pipeline:

1. A FastAPI service exposes domain data through documented endpoints.
2. Airflow DAGs orchestrate extraction and loading workflows.
3. SQLite stores curated analytics-ready tables.
4. Streamlit provides an interactive data application for end users.
5. Notebooks support exploratory analysis and experimentation.

## Repository Structure

```
analytics-project/
├── api/                  # FastAPI application, database models, CRUD, tests
├── airflow/              # Airflow orchestration project and pipeline docs
├── streamlit/            # Streamlit UI for roster and team analytics
├── notebooks/            # Jupyter notebook workflows and helper client
├── LICENSE
└── README.md
```

## What I Built

### 1. API Layer (FastAPI)

In [api/main.py](api/main.py), I implemented a read-focused REST API for players, performances, leagues, teams, weeks, and aggregate counts.

Key highlights:
- OpenAPI-friendly endpoint metadata (summaries, descriptions, tags, operation IDs).
- Query-based filtering with pagination and optional parameters.
- Dependency-injected SQLAlchemy sessions.
- Structured schema validation using Pydantic models.
- Test coverage in [api/test_main.py](api/test_main.py) and [api/test_crud.py](api/test_crud.py).

### 2. Pipeline Orchestration (Airflow)

In [airflow/readme.md](airflow/readme.md), the orchestration layer documents multi-DAG ingestion and upsert workflows into SQLite.

Key highlights:
- Multiple ingestion DAGs for leagues, teams, weeks, players, and bulk file loads.
- Shared upsert logic for repeatable, idempotent loads.
- Health-check-first execution patterns before data pulls.
- Runtime connection configuration for API + SQLite targets.

### 3. Analytics App (Streamlit)

The Streamlit frontend in [streamlit/streamlit_football_app.py](streamlit/streamlit_football_app.py) and [streamlit/page1.py](streamlit/page1.py) presents roster views and cross-league filtering.

Key highlights:
- Multi-page navigation architecture.
- Sidebar controls and league-level filtering.
- Data flattening and normalization for tabular display.
- Streamlit caching for API-backed data retrieval to improve rerun performance.
- Three built-in Streamlit visualizations on the Team Stats page:
	- `st.bar_chart` for team roster size by team.
	- `st.area_chart` for player position distribution.
	- `st.line_chart` for player profile update trends by date.
- Logging and exception handling for better supportability.

### 4. Exploratory Analytics (Notebooks)

The notebook workflow in [notebooks/shark_league_notebook.ipynb](notebooks/shark_league_notebook.ipynb) supports data exploration and iterative analysis.

## Engineering Customizations and Debugging Work

A major part of this project was not just building features, but diagnosing and resolving real integration issues across services.

Notable customizations and fixes:
- Fixed cross-service networking assumptions when containers accessed API services.
- Completed and aligned SQLite schema expectations with DAG upsert logic.
- Added robust handling paths in ingestion workflows to improve operational reliability.
- Corrected Streamlit API base URL normalization to prevent protocol-related request failures.
- Implemented Streamlit cache-backed API helpers to reduce repetitive HTTP requests.
- Expanded the Streamlit analytics page with built-in charts for faster, cleaner data storytelling.
- Improved UI resilience by pairing log-driven troubleshooting with user-facing fallback messaging.

These changes made the project substantially more production-like by reducing brittle assumptions and improving end-to-end reliability.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Apache Airflow
- Streamlit
- SQLite
- Pandas
- Docker / Docker Compose
- Pytest

## How to Run (High Level)

### API
- Enter [api](api)
- Install dependencies from [api/requirements.txt](api/requirements.txt)
- Run the FastAPI service

### Airflow
- Enter [airflow](airflow)
- Start services with Docker Compose
- Trigger DAGs from Airflow UI or CLI

### Streamlit
- Enter [streamlit](streamlit)
- Start the app with `streamlit run streamlit_football_app.py`
- Ensure the API is running before opening the app

## Streamlit Enhancements

Recent Streamlit improvements include performance optimization and richer visual storytelling:

- Cached API fetches implemented in [streamlit/swc_simple_client.py](streamlit/swc_simple_client.py) using `st.cache_data` (TTL-based).
- Team Rosters page updated to consume cached API responses in [streamlit/page1.py](streamlit/page1.py).
- Team Stats page rebuilt with three native Streamlit charts in [streamlit/page2.py](streamlit/page2.py):
	- Team roster sizes (`st.bar_chart`)
	- Position mix by selected league (`st.area_chart`)
	- Player update trend over time (`st.line_chart`)

## Portfolio Value

This project demonstrates practical, job-relevant data engineering capabilities:
- Designing and documenting production-style APIs.
- Building maintainable orchestration pipelines.
- Modeling and persisting analytical datasets.
- Shipping user-facing analytical applications.
- Debugging distributed issues across UI, API, scheduler, and storage layers.

## Additional Documentation

- API notes: [api/readme.md](api/readme.md)
- Airflow pipeline details: [airflow/readme.md](airflow/readme.md)
- Airflow execution summary: [airflow/FINAL_STATUS.md](airflow/FINAL_STATUS.md)

---

If you are reviewing this repository for hiring or collaboration, I recommend starting with the API and Airflow components, then opening the Streamlit app to see the integrated workflow in action.