import os
import sqlite3
import pandas as pd

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DOCS_DIR = os.path.join(BASE_DIR, "data", "documentation")

os.makedirs(DOCS_DIR, exist_ok=True)

REPORT_PATH = os.path.join(DOCS_DIR, "data_quality_report.txt")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def section(title):
    return f"\n{'=' * 70}\n{title}\n{'=' * 70}\n"


def missing_summary(df):
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        return "No missing values."

    return missing.to_string()


def duplicate_summary(df):
    return f"Duplicate rows: {df.duplicated().sum()}"


def categorical_summary(df, columns):
    output = []

    for col in columns:
        if col in df.columns:
            output.append(f"\n--- {col} ---")
            output.append(df[col].value_counts(dropna=False).head(20).to_string())

    return "\n".join(output)


# ============================================================
# IT DATASET ANALYSIS
# ============================================================

def analyze_it(report):
    report.append(section("1. IT DATASETS"))

    it_dir = os.path.join(RAW_DIR, "it")

    files = [
        "aa_dataset-tickets-multi-lang-5-2-50-version.csv",
        "dataset-tickets-multi-lang-4-20k.csv",
        "dataset-tickets-multi-lang3-4k.csv",
    ]

    dataframes = {}

    for filename in files:
        path = os.path.join(it_dir, filename)

        report.append(f"\nFILE: {filename}")

        # Read full CSV
        df = pd.read_csv(path)

        dataframes[filename] = df

        report.append(f"Rows: {len(df):,}")
        report.append(f"Columns: {len(df.columns)}")

        report.append("\nColumns:")
        report.append(", ".join(df.columns))

        report.append("\nData types:")
        report.append(df.dtypes.to_string())

        report.append("\nMissing values:")
        report.append(missing_summary(df))

        report.append(f"\nDuplicate rows: {df.duplicated().sum():,}")

        important_columns = [
            "type",
            "queue",
            "priority",
            "language",
            "version",
            "business_type",
        ]

        report.append("\nImportant categorical values:")
        report.append(categorical_summary(df, important_columns))

        tag_columns = [col for col in df.columns if col.startswith("tag_")]

        report.append("\nTag frequencies:")

        for tag in tag_columns:
            report.append(f"\n{tag}:")
            report.append(
                df[tag]
                .value_counts(dropna=False)
                .head(15)
                .to_string()
            )

    # --------------------------------------------------------
    # Compare IT schemas
    # --------------------------------------------------------

    report.append(section("IT SCHEMA COMPARISON"))

    for filename, df in dataframes.items():
        report.append(f"\n{filename}")
        report.append(f"Number of columns: {len(df.columns)}")
        report.append(f"Columns: {list(df.columns)}")

    # --------------------------------------------------------
    # Possible overlap between datasets
    # --------------------------------------------------------

    report.append(section("IT DATASET OVERLAP CHECK"))

    for i in range(len(files)):
        for j in range(i + 1, len(files)):

            file1 = files[i]
            file2 = files[j]

            df1 = dataframes[file1]
            df2 = dataframes[file2]

            common_columns = list(
                set(df1.columns).intersection(set(df2.columns))
            )

            report.append(
                f"\n{file1} <-> {file2}"
            )

            report.append(
                f"Common columns: {common_columns}"
            )

            if common_columns:
                # Use a few important columns to estimate possible overlap
                candidate_columns = [
                    col for col in [
                        "subject",
                        "body",
                        "answer"
                    ]
                    if col in common_columns
                ]

                if candidate_columns:
                    merged = df1[candidate_columns].merge(
                        df2[candidate_columns],
                        how="inner"
                    )

                    report.append(
                        f"Exact matches using "
                        f"{candidate_columns}: {len(merged):,}"
                    )
                else:
                    report.append(
                        "No suitable common text columns for overlap check."
                    )


# ============================================================
# RETAIL DATASET ANALYSIS
# ============================================================

def analyze_retail(report):
    report.append(section("2. RETAIL DATASET"))

    path = os.path.join(
        RAW_DIR,
        "retail",
        "Retail-Supply-Chain-Sales-Dataset.xlsx"
    )

    excel = pd.ExcelFile(path)

    report.append(f"Sheets: {excel.sheet_names}")

    for sheet in excel.sheet_names:

        report.append(f"\n{'-' * 60}")
        report.append(f"SHEET: {sheet}")
        report.append(f"{'-' * 60}")

        df = pd.read_excel(path, sheet_name=sheet)

        report.append(f"Rows: {len(df):,}")
        report.append(f"Columns: {len(df.columns)}")

        report.append("\nColumns:")
        report.append(", ".join(df.columns))

        report.append("\nData types:")
        report.append(df.dtypes.to_string())

        report.append("\nMissing values:")
        report.append(missing_summary(df))

        report.append(f"\nDuplicate rows: {df.duplicated().sum():,}")

        # Main retail sheet analysis
        if sheet == "Retails Order Full Dataset":

            important_columns = [
                "Ship Mode",
                "Segment",
                "Country",
                "Region",
                "Category",
                "Sub-Category",
                "Returned",
            ]

            report.append("\nImportant categorical values:")
            report.append(
                categorical_summary(df, important_columns)
            )

            report.append("\nUnique counts:")

            for col in [
                "Order ID",
                "Customer ID",
                "Product ID",
                "Customer Name",
                "Product Name",
            ]:
                if col in df.columns:
                    report.append(
                        f"{col}: {df[col].nunique(dropna=True):,}"
                    )

            # Date analysis
            for col in ["Order Date", "Ship Date"]:
                if col in df.columns:
                    dates = pd.to_datetime(
                        df[col],
                        errors="coerce"
                    )

                    report.append(
                        f"\n{col} range: "
                        f"{dates.min()} -> {dates.max()}"
                    )

            # Numerical analysis
            numerical_columns = [
                "Sales",
                "Quantity",
                "Discount",
                "Profit",
            ]

            report.append("\nNumerical summaries:")

            for col in numerical_columns:
                if col in df.columns:
                    report.append(f"\n{col}:")
                    report.append(
                        df[col].describe().to_string()
                    )

            # Potential data-quality issues
            report.append("\nPotential data-quality checks:")

            if "Quantity" in df.columns:
                report.append(
                    f"Zero quantity: "
                    f"{(df['Quantity'] == 0).sum():,}"
                )

                report.append(
                    f"Negative quantity: "
                    f"{(df['Quantity'] < 0).sum():,}"
                )

            if "Profit" in df.columns:
                report.append(
                    f"Negative profit: "
                    f"{(df['Profit'] < 0).sum():,}"
                )

            if "Discount" in df.columns:
                report.append(
                    f"Discount < 0: "
                    f"{(df['Discount'] < 0).sum():,}"
                )

                report.append(
                    f"Discount > 1: "
                    f"{(df['Discount'] > 1).sum():,}"
                )


# ============================================================
# AIRLINE DATABASE ANALYSIS
# ============================================================

def analyze_airline(report):
    report.append(section("3. AIRLINE DATABASE"))

    path = os.path.join(
        RAW_DIR,
        "airline",
        "travel.sqlite"
    )

    conn = sqlite3.connect(path)

    cursor = conn.cursor()

    tables = cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
        """
    ).fetchall()

    report.append(
        f"Number of tables: {len(tables)}"
    )

    for (table_name,) in tables:

        report.append(f"\n{'-' * 60}")
        report.append(f"TABLE: {table_name}")
        report.append(f"{'-' * 60}")

        # Row count
        count = cursor.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        ).fetchone()[0]

        report.append(f"Rows: {count:,}")

        # Columns
        columns = cursor.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()

        report.append("\nColumns:")

        for col in columns:
            cid, name, dtype, notnull, default, pk = col

            report.append(
                f"{name} | type={dtype} | "
                f"not_null={notnull} | pk={pk}"
            )

        # NULL counts
        report.append("\nNULL counts:")

        for col in columns:
            column_name = col[1]

            null_count = cursor.execute(
                f'''
                SELECT COUNT(*)
                FROM "{table_name}"
                WHERE "{column_name}" IS NULL
                '''
            ).fetchone()[0]

            if null_count > 0:
                report.append(
                    f"{column_name}: {null_count:,}"
                )

        # Foreign keys
        foreign_keys = cursor.execute(
            f'PRAGMA foreign_key_list("{table_name}")'
        ).fetchall()

        report.append("\nForeign keys:")

        if foreign_keys:
            for fk in foreign_keys:
                report.append(str(fk))
        else:
            report.append("No declared foreign keys.")

    conn.close()


# ============================================================
# MAIN
# ============================================================

def main():

    report = []

    report.append(
        "TEXT-TO-SQL DATA QUALITY REPORT"
    )

    report.append(
        f"\nProject directory:\n{BASE_DIR}"
    )

    analyze_it(report)
    analyze_retail(report)
    analyze_airline(report)

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        file.write("\n".join(report))

    print("\nAnalysis completed successfully.")
    print(f"Report saved to:\n{REPORT_PATH}")


if __name__ == "__main__":
    main()