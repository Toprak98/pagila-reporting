import psycopg2
import pandas as pd

def get_connection(host: str, database: str, user: str, password: str, port: int = 5432):
    return psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )

def run_query(conn, sql: str, params=None) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)
