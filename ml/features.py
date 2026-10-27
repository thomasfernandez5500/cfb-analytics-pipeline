"""
Pulls the fct_games mart out of the warehouse and builds the X/y matrices
for training. Kept separate from train_model.py so predict.py can reuse it.
"""
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

WAREHOUSE = os.environ.get("WAREHOUSE", "bigquery").lower()

FEATURE_COLUMNS = ["spread", "over_under", "week"]  # TODO: expand with recruiting/advanced stats
TARGET_COLUMN = "home_team_won"


def load_fct_games() -> pd.DataFrame:
    query = "select * from fct_games"  # dbt marts schema/dataset is set in profiles.yml
    if WAREHOUSE == "bigquery":
        from google.cloud import bigquery
        project = os.environ["BIGQUERY_PROJECT"]
        dataset = os.environ.get("BIGQUERY_DATASET", "cfb_analytics")
        client = bigquery.Client(project=project)
        return client.query(f"select * from `{project}.{dataset}.fct_games`").to_dataframe()
    elif WAREHOUSE == "snowflake":
        import snowflake.connector
        conn = snowflake.connector.connect(
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            user=os.environ["SNOWFLAKE_USER"],
            password=os.environ["SNOWFLAKE_PASSWORD"],
            warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            database=os.environ.get("SNOWFLAKE_DATABASE", "CFB_ANALYTICS"),
        )
        try:
            cur = conn.cursor()
            cur.execute("select * from fct_games")
            return cur.fetch_pandas_all()
        finally:
            conn.close()
    else:
        raise ValueError(f"Unknown WAREHOUSE '{WAREHOUSE}'")


def build_training_set():
    df = load_fct_games().dropna(subset=[TARGET_COLUMN])
    X = df[FEATURE_COLUMNS].fillna(0)
    y = df[TARGET_COLUMN].astype(int)
    return X, y
