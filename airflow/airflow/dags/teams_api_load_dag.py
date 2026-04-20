import datetime
import logging
from airflow.decorators import dag
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
from shared_functions import upsert_team_data

# verify the response of api_health_check_task
def health_check_response(response):
    logging.info(f"Response status code: {response.status_code}")
    logging.info(f"Response body: {response.text}")
    return response.status_code == 200 and response.json() == {"message": "API health check successful"}

# define the function to insert/update team data in SQLite database
def insert_update_team_data(**context):
    team_json = context['ti'].xcom_pull(task_ids='api_team_query')
    if team_json:
        upsert_team_data(team_json)
    else:
        logging.warning("No team data found.")

# main DAG definition      
@dag(start_date=datetime.datetime(2024, 4, 1), schedule_interval=None, catchup=False)
def teams_api_load_dag():
    # call the API health check endpoint
    api_health_check_task = HttpOperator(
        task_id="check_api_health_check_endpoint",
        http_conn_id="sportsworldcentral_url",
        endpoint="/",
        method="GET",
        headers={"Content-Type": "application/json"},
        response_check=health_check_response,
    )
    
    # call the API teams endpoint
    api_team_query_task = HttpOperator(
        task_id="api_team_query",
        http_conn_id="sportsworldcentral_url",
        endpoint="/v0/teams/?skip=0&limit=100000",
        method="GET",
        headers={"Content-Type": "application/json"},
    )
    
    # call the function to insert/update team data in SQLite database
    team_sqlite_upsert_task = PythonOperator(
        task_id="team_sqlite_upsert",
        python_callable=insert_update_team_data,
        provide_context=True,
    )
    
    # set the dependency of the tasks
    api_health_check_task >> api_team_query_task >> team_sqlite_upsert_task
    
# Instantiate the DAG
dag_instance = teams_api_load_dag()
