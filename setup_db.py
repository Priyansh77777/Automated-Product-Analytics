"""Load ecommerce_data.csv into a local SQLite database."""

from pathlib import Path

import pandas as pd
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "ecommerce_data.csv"
DB_PATH = BASE_DIR / "product_metrics.db"
TABLE_NAME = "user_transactions"


def main() -> None:
    print(f"Reading CSV from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df):,} rows and {len(df.columns)} columns.")

    print(f"Writing to SQLite database: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        row_count = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]

    print(f"Saved {row_count:,} rows into table '{TABLE_NAME}'.")
    print("Database setup succeeded.")


if __name__ == "__main__":
    main()
