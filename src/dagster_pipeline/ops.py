import subprocess
import os
from dagster import op, get_dagster_logger, OpExecutionContext

logger = get_dagster_logger()

# Define common environment variables for scripts.
# These will be passed from the Docker environment to the ops' subprocesses.
# Using os.getenv directly in the op's execution context is more robust
# as Dagster ensures these are available.
# We'll pass os.environ directly to subprocess.run to inherit all Docker env vars.

@op
def scrape_telegram_data(context: OpExecutionContext):
    """
    Dagster op to execute the Telegram data scraping script.
    """
    context.log.info("Starting Telegram data scraping...")
    try:
        result = subprocess.run(
            ["python", "scripts/scrape_telegram.py"],
            cwd="/app", # Run from /app to find scripts/
            capture_output=True,
            text=True,
            check=True, # Raise an exception if the command returns a non-zero exit code
            env=os.environ # Pass all environment variables from the container
        )
        context.log.info(f"Scraping stdout:\n{result.stdout}")
        if result.stderr:
            context.log.error(f"Scraping stderr:\n{result.stderr}")
        context.log.info("Telegram data scraping completed successfully.")
    except subprocess.CalledProcessError as e:
        context.log.error(f"Scraping failed with error: {e.stderr}")
        raise
    except Exception as e:
        context.log.error(f"An unexpected error occurred during scraping: {e}")
        raise

@op
def load_raw_to_postgres(context: OpExecutionContext):
    """
    Dagster op to execute the raw data loading script to PostgreSQL.
    """
    context.log.info("Starting raw data loading to PostgreSQL...")
    try:
        result = subprocess.run(
            ["python", "scripts/load_to_postgres.py"],
            cwd="/app",
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        )
        context.log.info(f"Loading stdout:\n{result.stdout}")
        if result.stderr:
            context.log.error(f"Loading stderr:\n{result.stderr}")
        context.log.info("Raw data loading to PostgreSQL completed successfully.")
    except subprocess.CalledProcessError as e:
        context.log.error(f"Loading failed with error: {e.stderr}")
        raise
    except Exception as e:
        context.log.error(f"An unexpected error occurred during loading: {e}")
        raise

@op
def run_yolo_enrichment(context: OpExecutionContext):
    """
    Dagster op to execute the YOLO object detection enrichment script.
    """
    context.log.info("Starting YOLO object detection enrichment...")
    try:
        result = subprocess.run(
            ["python", "scripts/detect_objects.py"],
            cwd="/app",
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        )
        context.log.info(f"YOLO enrichment stdout:\n{result.stdout}")
        if result.stderr:
            context.log.error(f"YOLO enrichment stderr:\n{result.stderr}")
        context.log.info("YOLO object detection enrichment completed successfully.")
    except subprocess.CalledProcessError as e:
        context.log.error(f"YOLO enrichment failed with error: {e.stderr}")
        raise
    except Exception as e:
        context.log.error(f"An unexpected error occurred during YOLO enrichment: {e}")
        raise

@op
def run_dbt_transformations(context: OpExecutionContext):
    """
    Dagster op to execute dbt commands for transformations and tests.
    Includes dbt clean, run, and test.
    """
    context.log.info("Starting dbt transformations...")
    dbt_commands = [
        ["dbt", "debug"], # Good for initial connection check
        ["dbt", "clean"],
        ["dbt", "run"],
        ["dbt", "test"]
    ]
    dbt_cwd = "/app/src/dbt" # dbt commands must be run from the dbt project directory

    try:
        for cmd in dbt_commands:
            command_str = " ".join(cmd)
            context.log.info(f"Executing dbt command: {command_str}")
            result = subprocess.run(
                cmd,
                cwd=dbt_cwd,
                capture_output=True,
                text=True,
                check=True,
                env=os.environ
            )
            context.log.info(f"dbt {cmd[1]} stdout:\n{result.stdout}")
            if result.stderr:
                context.log.error(f"dbt {cmd[1]} stderr:\n{result.stderr}")
        context.log.info("dbt transformations and tests completed successfully.")
    except subprocess.CalledProcessError as e:
        context.log.error(f"dbt command '{' '.join(e.cmd)}' failed with error: {e.stderr}")
        raise
    except Exception as e:
        context.log.error(f"An unexpected error occurred during dbt transformations: {e}")
        raise

