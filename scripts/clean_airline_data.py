import sqlite3
import pandas as pd
from pathlib import Path


RAW_FILE = Path("data/raw/airline/travel.sqlite")
OUTPUT_DIR = Path("data/processed/airline")


TABLES = [
    "aircrafts_data",
    "airports_data",
    "seats",
    "bookings",
    "tickets",
    "flights",
    "ticket_flights",
    "boarding_passes",
]


def main():
    print("=" * 80)
    print("AIRLINE DATA CLEANING")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. CONNECT TO SQLITE
    # ------------------------------------------------------------------
    conn = sqlite3.connect(RAW_FILE)

    print(f"Source database: {RAW_FILE}")
    print()

    # ------------------------------------------------------------------
    # 2. EXTRACT TABLES
    # ------------------------------------------------------------------
    for table in TABLES:
        print(f"Reading table: {table}")

        df = pd.read_sql_query(
            f'SELECT * FROM "{table}"',
            conn
        )

        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        # ------------------------------------------------------------------
        # 3. STANDARDIZE TABLE NAMES / COLUMN NAMES
        # ------------------------------------------------------------------
        output_name = table

        if table == "aircrafts_data":
            output_name = "aircrafts"

        elif table == "airports_data":
            output_name = "airports"

        # Remove leading/trailing whitespace from column names
        df.columns = df.columns.str.strip()

        # Remove leading/trailing whitespace from text values
        for column in df.select_dtypes(include=["object"]).columns:
            df[column] = df[column].astype("string").str.strip()

        # ------------------------------------------------------------------
        # 4. SAVE CSV
        # ------------------------------------------------------------------
        output_file = OUTPUT_DIR / f"{output_name}.csv"

        df.to_csv(
            output_file,
            index=False
        )

        print(f"Saved: {output_file}")
        print()

    conn.close()

    # ------------------------------------------------------------------
    # 5. SUMMARY
    # ------------------------------------------------------------------
    print("=" * 80)
    print("AIRLINE EXTRACTION COMPLETE")
    print("=" * 80)

    for table in TABLES:
        output_name = table

        if table == "aircrafts_data":
            output_name = "aircrafts"

        elif table == "airports_data":
            output_name = "airports"

        print(
            f"{output_name}.csv"
        )


if __name__ == "__main__":
    main()