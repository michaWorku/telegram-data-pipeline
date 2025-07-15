from dagster import job
from .ops import (
    scrape_telegram_data,
    load_raw_to_postgres,
    run_yolo_enrichment,
    run_dbt_transformations,
)

@job(description="Orchestrates the full Telegram data ETL and enrichment pipeline.")
def telegram_etl_pipeline():
    """
    The main ETL pipeline job for Telegram data.
    Dependencies:
    - scrape_telegram_data -> load_raw_to_postgres
    - load_raw_to_postgres -> run_yolo_enrichment
    - run_yolo_enrichment -> run_dbt_transformations
    """
    # Define the dependencies between ops using the .after() method for clarity
    # or by passing outputs as inputs if data is explicitly passed between ops.
    # Here, we use start_after for sequential execution without explicit data passing.

    scraped_data_result = scrape_telegram_data()
    loaded_data_result = load_raw_to_postgres(start_after=scraped_data_result)
    enriched_data_result = run_yolo_enrichment(start_after=loaded_data_result)
    run_dbt_transformations(start_after=enriched_data_result)

