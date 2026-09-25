import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
REPORT_DIR = os.path.join(BASE_DIR, "data", "documentation")

os.makedirs(REPORT_DIR, exist_ok=True)

report = []


def add(text=""):
    print(text)
    report.append(text)


def section(title):
    add("\n" + "=" * 80)
    add(title)
    add("=" * 80)


# ============================================================
# IT DATASET RELATIONSHIP ANALYSIS
# ============================================================

section("1. IT DATASET RELATIONSHIP ANALYSIS")

it_files = [
    "aa_dataset-tickets-multi-lang-5-2-50-version.csv",
    "dataset-tickets-multi-lang-4-20k.csv",
    "dataset-tickets-multi-lang3-4k.csv",
]

it_data = {}

for filename in it_files:
    path = os.path.join(RAW_DIR, "it", filename)
    df = pd.read_csv(path)
    it_data[filename] = df

    add(f"\nDataset: {filename}")
    add(f"Rows: {len(df)}")

    # Candidate uniqueness
    for col in ["subject", "body", "answer"]:
        if col in df.columns:
            add(
                f"{col}: unique={df[col].nunique(dropna=False)}, "
                f"duplicates={df[col].duplicated().sum()}"
            )

    # Check possible natural key combinations
    available = [c for c in ["subject", "body", "answer"] if c in df.columns]

    if available:
        duplicate_key_rows = df.duplicated(subset=available).sum()
        add(
            f"Duplicate rows based on {available}: "
            f"{duplicate_key_rows}"
        )

# Compare first two IT datasets more deeply
section("1A. IT DATASET 1 vs DATASET 2 OVERLAP")

df1 = it_data[it_files[0]]
df2 = it_data[it_files[1]]

common_key = ["subject", "body", "answer"]

merged = df1.merge(
    df2,
    on=common_key,
    how="inner",
    suffixes=("_d1", "_d2")
)

add(f"Matching records using subject + body + answer: {len(merged)}")

if len(merged) > 0:
    for col in ["type", "queue", "priority", "language"]:
        c1 = f"{col}_d1"
        c2 = f"{col}_d2"

        if c1 in merged.columns and c2 in merged.columns:
            same = (merged[c1].fillna("") == merged[c2].fillna("")).sum()
            different = len(merged) - same

            add(
                f"{col}: same={same}, different={different}"
            )

# Dataset 3 comparison
section("1B. IT DATASET 3 RELATIONSHIP")

df3 = it_data[it_files[2]]

merged_13 = df1.merge(
    df3,
    on=common_key,
    how="inner"
)

merged_23 = df2.merge(
    df3,
    on=common_key,
    how="inner"
)

add(f"Dataset 1 vs Dataset 3 matching records: {len(merged_13)}")
add(f"Dataset 2 vs Dataset 3 matching records: {len(merged_23)}")

# ============================================================
# RETAIL DATASET RELATIONSHIP ANALYSIS
# ============================================================

section("2. RETAIL DATASET RELATIONSHIP ANALYSIS")

retail_path = os.path.join(
    RAW_DIR,
    "retail",
    "Retail-Supply-Chain-Sales-Dataset.xlsx"
)

retail = pd.read_excel(
    retail_path,
    sheet_name="Retails Order Full Dataset"
)

add(f"Rows: {len(retail)}")

candidate_columns = [
    "Row ID",
    "Order ID",
    "Customer ID",
    "Customer Name",
    "Product ID",
    "Product Name",
]

add("\nCandidate key uniqueness:")

for col in candidate_columns:
    if col in retail.columns:
        add(
            f"{col}: unique={retail[col].nunique()}, "
            f"duplicates={retail[col].duplicated().sum()}"
        )

# Check one-to-one relationships
section("2A. RETAIL ATTRIBUTE CONSISTENCY")

checks = [
    ("Customer ID", "Customer Name"),
    ("Product ID", "Product Name"),
]

for key, value in checks:
    mapping_counts = retail.groupby(key)[value].nunique()

    inconsistent = (mapping_counts > 1).sum()

    add(
        f"{key} -> {value}: "
        f"inconsistent keys={inconsistent}"
    )

# Order relationship
order_line_counts = retail.groupby("Order ID")["Row ID"].count()

add(
    f"\nOrders with multiple order lines: "
    f"{(order_line_counts > 1).sum()}"
)

add(
    f"Maximum lines for one order: "
    f"{order_line_counts.max()}"
)

# Row ID uniqueness
add(
    f"Row ID unique: "
    f"{retail['Row ID'].is_unique}"
)

# ============================================================
# AIRLINE DATABASE RELATIONSHIP ANALYSIS
# ============================================================

section("3. AIRLINE DATABASE RELATIONSHIP ANALYSIS")

airline_path = os.path.join(
    RAW_DIR,
    "airline",
    "travel.sqlite"
)

conn = sqlite3.connect(airline_path)

tables = [
    "aircrafts_data",
    "airports_data",
    "boarding_passes",
    "bookings",
    "flights",
    "seats",
    "ticket_flights",
    "tickets",
]

airline_data = {}

for table in tables:
    df = pd.read_sql_query(
        f'SELECT * FROM "{table}"',
        conn
    )
    airline_data[table] = df

    add(f"\n{table}: {len(df)} rows")

    # Candidate key checks
    if table == "aircrafts_data":
        col = "aircraft_code"
        add(f"{col} unique: {df[col].is_unique}")

    elif table == "airports_data":
        col = "airport_code"
        add(f"{col} unique: {df[col].is_unique}")

    elif table == "bookings":
        col = "book_ref"
        add(f"{col} unique: {df[col].is_unique}")

    elif table == "tickets":
        col = "ticket_no"
        add(f"{col} unique: {df[col].is_unique}")

    elif table == "flights":
        col = "flight_id"
        add(f"{col} unique: {df[col].is_unique}")

    elif table == "seats":
        cols = ["aircraft_code", "seat_no"]
        add(
            f"{cols} unique combination: "
            f"{not df.duplicated(subset=cols).any()}"
        )

# ============================================================
# AIRLINE FOREIGN KEY VALIDATION
# ============================================================

section("3A. AIRLINE FOREIGN KEY VALIDATION")

def check_reference(child_df, child_col, parent_df, parent_col, name):
    child_values = set(child_df[child_col].dropna())
    parent_values = set(parent_df[parent_col].dropna())

    invalid = child_values - parent_values

    add(
        f"{name}: invalid references={len(invalid)}"
    )


check_reference(
    airline_data["tickets"],
    "book_ref",
    airline_data["bookings"],
    "book_ref",
    "tickets.book_ref -> bookings.book_ref"
)

check_reference(
    airline_data["ticket_flights"],
    "ticket_no",
    airline_data["tickets"],
    "ticket_no",
    "ticket_flights.ticket_no -> tickets.ticket_no"
)

check_reference(
    airline_data["ticket_flights"],
    "flight_id",
    airline_data["flights"],
    "flight_id",
    "ticket_flights.flight_id -> flights.flight_id"
)

check_reference(
    airline_data["flights"],
    "aircraft_code",
    airline_data["aircrafts_data"],
    "aircraft_code",
    "flights.aircraft_code -> aircrafts_data.aircraft_code"
)

check_reference(
    airline_data["flights"],
    "departure_airport",
    airline_data["airports_data"],
    "airport_code",
    "flights.departure_airport -> airports_data.airport_code"
)

check_reference(
    airline_data["flights"],
    "arrival_airport",
    airline_data["airports_data"],
    "airport_code",
    "flights.arrival_airport -> airports_data.airport_code"
)

# Boarding pass -> ticket_flights composite relationship
bp = airline_data["boarding_passes"]
tf = airline_data["ticket_flights"]

valid_pairs = set(
    zip(
        tf["ticket_no"],
        tf["flight_id"]
    )
)

boarding_pairs = list(
    zip(
        bp["ticket_no"],
        bp["flight_id"]
    )
)

invalid_boarding = sum(
    pair not in valid_pairs
    for pair in boarding_pairs
)

add(
    "boarding_passes.(ticket_no, flight_id) -> "
    f"ticket_flights.(ticket_no, flight_id): "
    f"invalid references={invalid_boarding}"
)

# Boarding pass -> seats relationship
seats = airline_data["seats"]
flights = airline_data["flights"]

# Add aircraft_code to each boarding pass using flight_id
bp_check = bp[["ticket_no", "flight_id", "seat_no"]].merge(
    flights[["flight_id", "aircraft_code"]],
    on="flight_id",
    how="left"
)

# Create valid (aircraft_code, seat_no) combinations
valid_seats = set(
    zip(
        seats["aircraft_code"],
        seats["seat_no"]
    )
)

# Create boarding pass seat combinations
boarding_seat_pairs = list(
    zip(
        bp_check["aircraft_code"],
        bp_check["seat_no"]
    )
)

invalid_seats = sum(
    pair not in valid_seats
    for pair in boarding_seat_pairs
)

add(
    "boarding_passes -> seats through "
    "(flight_id -> aircraft_code, seat_no): "
    f"invalid references={invalid_seats}"
)
# ============================================================
# AIRLINE VALUE CHECKS
# ============================================================

section("3B. AIRLINE IMPORTANT VALUES")

for col in ["status"]:
    if col in airline_data["flights"].columns:
        add(
            f"Flight status values: "
            f"{airline_data['flights'][col].value_counts().to_dict()}"
        )

if "fare_conditions" in airline_data["seats"].columns:
    add(
        f"Seat fare conditions: "
        f"{airline_data['seats']['fare_conditions'].value_counts().to_dict()}"
    )

if "fare_conditions" in airline_data["ticket_flights"].columns:
    add(
        f"Ticket flight fare conditions: "
        f"{airline_data['ticket_flights']['fare_conditions'].value_counts().to_dict()}"
    )

# Null counts for important airline fields
section("3C. AIRLINE IMPORTANT NULLS")

for table, columns in {
    "flights": [
        "actual_departure",
        "actual_arrival",
    ],
    "boarding_passes": [
        "seat_no",
    ],
}.items():

    df = airline_data[table]

    for col in columns:
        add(
            f"{table}.{col} nulls: "
            f"{df[col].isna().sum()}"
        )

conn.close()

# ============================================================
# SAVE REPORT
# ============================================================

output_path = os.path.join(
    REPORT_DIR,
    "relationship_analysis_report.txt"
)

with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print("\n" + "=" * 80)
print(f"Report saved to: {output_path}")
print("=" * 80)