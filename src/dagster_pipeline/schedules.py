from dagster import schedule
from .jobs import telegram_etl_pipeline

@schedule(
    cron_schedule="0 0 * * *", # Run daily at midnight UTC
    job=telegram_etl_pipeline,
    execution_timezone="UTC",
    description="Daily schedule for the Telegram ETL and enrichment pipeline."
)
def daily_telegram_etl_schedule(context):
    """
    A daily schedule that kicks off the telegram_etl_pipeline job.
    """
    # You can pass run_config here if your job has configurable parameters
    return {}

