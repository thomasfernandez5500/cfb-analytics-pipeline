"""
Loads a pandas DataFrame into whichever warehouse is selected via the
WAREHOUSE env var ("bigquery" or "snowflake"). Keeps ingestion scripts
warehouse-agnostic so you can switch without touching the pull logic.

TODO: this does a simple full-table replace per load for scaffold simplicity.
Swap to an incremental/merge strategy once the pipeline is running on a
schedule (dbt's incremental materialization handles this better long-term —
consider loading raw JSON/parquet to a staging area and letting dbt do the
rest, rather than writing clean tables directly from Python).
"""
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

WAREHOUSE = os.environ.get("WAREHOUSE", "bigquery").lower()


def load_dataframe(df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> None:
    if df.empty:
        print(f"[warehouse_loader] Skipping load for {table_name}: empty dataframe")
        return

    if WAREHOUSE == "bigquery":
        _load_bigquery(df, table_name, if_exists)
    elif WAREHOUSE == "snowflake":
        _load_snowflake(df, table_name, if_exists)
    else:
        raise ValueError(f"Unknown WAREHOUSE '{WAREHOUSE}'. Use 'bigquery' or 'snowflake'.")


def _load_bigquery(df: pd.DataFrame, table_name: str, if_exists: str) -> None:
    from google.cloud import bigquery

    project = os.environ["BIGQUERY_PROJECT"]
    dataset = os.environ.get("BIGQUERY_DATASET", "cfb_raw")
    client = bigquery.Client(project=project)
    table_id = f"{project}.{dataset}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE" if if_exists == "replace" else "WRITE_APPEND",
        autodetect=True,
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"[warehouse_loader] Loaded {len(df)} rows into {table_id}")


def _load_snowflake(df: pd.DataFrame, table_name: str, if_exists: str) -> None:
    import snowflake.connector
    from snowflake.connector.pandas_tools import write_pandas

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "CFB_RAW"),
    )
    try:
        write_pandas(
            conn,
            df,
            table_name.upper(),
            auto_create_table=True,
            overwrite=(if_exists == "replace"),
        )
        print(f"[warehouse_loader] Loaded {len(df)} rows into {table_name.upper()}")
    finally:
        conn.close()
