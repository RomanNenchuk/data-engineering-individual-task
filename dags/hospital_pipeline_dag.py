from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.bash import BashOperator

# Базові налаштування для тасок
default_args = {
    'owner': 'roman_nenchuk',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Оголошуємо наш DAG
with DAG(
    'medical_infrastructure_pipeline',
    default_args=default_args,
    description='Комплексний пайплайн обробки та просторового аналізу медичних закладів',
    schedule_interval=None, # Запуск вручну через інтерфейс
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=['university', 'spatial_analysis'],
) as dag:

    # Визначаємо кроки нашого конвеєра за допомогою BashOperator
    
    # Крок 1: Запуск очищення даних (ETL)
    run_etl_task = BashOperator(
        task_id='run_etl_pipeline',
        bash_command='python /opt/airflow/scripts/etl_pipeline.py',
    )

    # Крок 2: Запуск кластеризації (DBSCAN)
    run_clustering_task = BashOperator(
        task_id='run_spatial_clustering',
        bash_command='python /opt/airflow/scripts/spatial_clustering.py',
    )

    # Крок 3: Генерація BI звіту (Інтерактивної карти)
    generate_map_task = BashOperator(
        task_id='generate_bi_map',
        bash_command='python /opt/airflow/scripts/bi_visualization.py',
    )

    # Встановлюємо чітку послідовність виконання (залежності)
    run_etl_task >> run_clustering_task >> generate_map_task
