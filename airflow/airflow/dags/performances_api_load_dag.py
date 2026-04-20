import datetime
import logging
from airflow.decorators import dag
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
from shared_functions import upsert_performance_data

# verify the response of api_health_check_task
def health_check_response(response):
    logging.info(f"Response status code: {response.status_code}")
    logging.info(f"Response body: {response.text}")
    return response.status_code == 200 and response.json() == {"message": "API health check successful"}

# define the function to insert/update performance data in SQLite database
def insert_update_performance_data(**context):
    performance_json = context['ti'].xcom_pull(task_ids='api_performance_query')
    if performance_json:
        upsert_performance_data(performance_json)
    else:
        logging.warning("No performance data found.")

# calculate minimum last changed date (7 days before execution date)
def calculate_min_date(**context):
    execution_date = context['execution_date']
    min_date = (execution_date - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    return min_date

# main DAG definition      
@dag(start_date=datetime.datetime(2024, 4, 1), schedule_interval=None, catchup=False)
def performances_api_load_dag():
    # call the API health check endpoint
    api_health_check_task = HttpOperator(
        task_id="check_api_health_check_endpoint",
        http_conn_id="sportsworldcentral_url",
        endpoint="/",
        method="GET",
        headers={"Content-Type": "application/json"},
        response_check=health_check_response,
    )
    
    # calculate the minimum date for filtering (7 days before execution)
    calculate_date_task = PythonOperator(
        task_id="calculate_min_date",
        python_callable=calculate_min_date,
        provide_context=True,
    )
    
    # call the API performances endpoint with a 7-day rolling window using dynamic date from previous task
    api_performance_query_task = HttpOperator(
        task_id="api_performance_query",
        http_conn_id="sportsworldcentral_url",
        endpoint="/v0/performances/?skip=0&limit=100000&minimum_last_changed_date={{ task_instance.xcom_pull(task_ids='calculate_min_date') }}",
        method="GET",
        headers={"Content-Type": "application/json"},
    )
    
    # call the function to insert/update performance data in SQLite database
    performance_sqlite_upsert_task = PythonOperator(
        task_id="performance_sqlite_upsert",
        python_callable=insert_update_performance_data,
        provide_context=True,
    )
    
    # set the dependency of the tasks
    api_health_check_task >> calculate_date_task >> api_performance_query_task >> performance_sqlite_upsert_task
    
# Instantiate the DAG
dag_instance = performances_api_load_dag()
