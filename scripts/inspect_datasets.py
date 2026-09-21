import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")


def inspect_csv(file_path):
    print("\n" + "=" * 70)
    print("CSV FILE:", os.path.basename(file_path))
    print("=" * 70)

    try:
        # Read only a sample so large files don't consume huge memory
        df = pd.read_csv(file_path, nrows=5000)

        print("Sample rows:", len(df))
        print("Columns:", len(df.columns))

        print("\nCOLUMN NAMES:")
        for column in df.columns:
            print(" -", column)

        print("\nDATA TYPES:")
        print(df.dtypes)

        print("\nMISSING VALUES IN SAMPLE:")
        print(df.isnull().sum())

        print("\nDUPLICATE ROWS IN SAMPLE:", df.duplicated().sum())

        print("\nFIRST 5 ROWS:")
        print(df.head().to_string())

    except Exception as e:
        print("ERROR:", e)


def inspect_excel(file_path):
    print("\n" + "=" * 70)
    print("EXCEL FILE:", os.path.basename(file_path))
    print("=" * 70)

    try:
        excel_file = pd.ExcelFile(file_path)

        print("SHEETS:")
        for sheet in excel_file.sheet_names:
            print(" -", sheet)

        for sheet in excel_file.sheet_names:
            print("\n" + "-" * 60)
            print("SHEET:", sheet)
            print("-" * 60)

            df = pd.read_excel(
                file_path,
                sheet_name=sheet,
                nrows=5000
            )

            print("Sample rows:", len(df))
            print("Columns:", len(df.columns))

            print("\nCOLUMN NAMES:")
            for column in df.columns:
                print(" -", column)

            print("\nDATA TYPES:")
            print(df.dtypes)

            print("\nMISSING VALUES IN SAMPLE:")
            print(df.isnull().sum())

            print("\nDUPLICATE ROWS IN SAMPLE:", df.duplicated().sum())

            print("\nFIRST 5 ROWS:")
            print(df.head().to_string())

    except Exception as e:
        print("ERROR:", e)


def inspect_sqlite(file_path):
    print("\n" + "=" * 70)
    print("SQLITE DATABASE:", os.path.basename(file_path))
    print("=" * 70)

    try:
        connection = sqlite3.connect(file_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )

        tables = cursor.fetchall()

        print("TABLES:")

        for table in tables:
            table_name = table[0]
            print("\n" + "-" * 60)
            print("TABLE:", table_name)
            print("-" * 60)

            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = cursor.fetchall()

            print("COLUMNS:")

            for column in columns:
                print(
                    f" - {column[1]} | Type: {column[2]} "
                    f"| Primary Key: {column[5]}"
                )

            cursor.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            )

            row_count = cursor.fetchone()[0]

            print("\nTOTAL ROWS:", row_count)

            sample = pd.read_sql_query(
                f'SELECT * FROM "{table_name}" LIMIT 5',
                connection
            )

            print("\nFIRST 5 ROWS:")
            print(sample.to_string())

        connection.close()

    except Exception as e:
        print("ERROR:", e)


def scan_directory():
    print("\n")
    print("=" * 70)
    print("TEXT-TO-SQL DATASET INSPECTION")
    print("=" * 70)

    for root, directories, files in os.walk(RAW_DIR):

        for filename in files:

            file_path = os.path.join(root, filename)
            extension = filename.lower().split(".")[-1]

            if extension == "csv":
                inspect_csv(file_path)

            elif extension in ["xlsx", "xls"]:
                inspect_excel(file_path)

            elif extension in ["sqlite", "db"]:
                inspect_sqlite(file_path)

            else:
                print("\nSkipping unsupported file:", filename)


if __name__ == "__main__":
    scan_directory()