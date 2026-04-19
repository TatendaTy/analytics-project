import datetime
import logging
from airflow.decorators import dag
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
from shared_functions import upsert_player_data

# verify the response of api_health_check_task
def health_check_response(response):
    logging.info(f"Response status code: {response.status_code}")
    logging.info(f"Response body: {response.text}")
    return response.status_code == 200 and response.json() == {"message": "API health check successful"}

# define the function to insert/update player data in SQLite database
def insert_update_player_data(**context):
    player_json = context['ti'].xcom_pull(task_ids='api_player_query') # use XCom to retrieve data from the second task
    if player_json:
        upsert_player_data(player_json) # pass the retrieved data to the upsert function
    else:
        logging.warning("No player data found.")

# main DAG definition      
@dag(start_date=datetime.datetime(2024, 4, 1), schedule_interval=None, catchup=False)
def recurring_player_api_insert_update_dag():
    # call the API health check endpoint to ensure the API is up and running before proceeding with data retrieval
    api_health_check_task = HttpOperator(
        task_id="check_api_health_check_endpoint",
        http_conn_id="sportsworldcentral_url",
        endpoint="/",
        method="GET",
        headers={"Content-Type": "application/json"},
        response_check=health_check_response,
    )
    
    # use Airflow template variable ds_add to dynamically calculate the minimum last change date
    # this retrieves changes from the last 7 days relative to the execution date
    
    # call the APIs player endpoint with a query parameter to restrict the records returned to those that have been changed
    # since 7 days ago (using Airflow's ds_add template variable), and use XCom to pass the retrieved data to the next task
    api_player_query_task = HttpOperator(
        task_id="api_player_query",
        http_conn_id="sportsworldcentral_url",
        endpoint="/v0/players/?skip=0&limit=100000&minimum_last_changed_date={{ ds_add(ds, -7) }}",
        method="GET",
        headers={"Content-Type": "application/json"},
        )
    
    # call the function to insert/update player data in SQLite database, and use XCom to retrieve the data from the previous task
    player_sqlite_upsert_task = PythonOperator(
        task_id="player_sqlite_upsert",
        python_callable=insert_update_player_data,
        provide_context=True,
    )
    
    # set the dependency of the tasks using bitshift operators to ensure they run in the correct order
    api_health_check_task >> api_player_query_task >> player_sqlite_upsert_task
    
# Instatiate the DAG
dag_instance = recurring_player_api_insert_update_dag()