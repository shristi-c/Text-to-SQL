import os
import pandas as pd

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DIR = os.path.join(BASE_DIR, "data", "raw", "it")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed", "it")

os.makedirs(PROCESSED_DIR, exist_ok=True)


# ============================================================
# FILES
# ============================================================

FILE_1 = "aa_dataset-tickets-multi-lang-5-2-50-version.csv"
FILE_2 = "dataset-tickets-multi-lang-4-20k.csv"
FILE_3 = "dataset-tickets-multi-lang3-4k.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 80)
print("IT DATA CLEANING")
print("=" * 80)

df1 = pd.read_csv(os.path.join(RAW_DIR, FILE_1))
df2 = pd.read_csv(os.path.join(RAW_DIR, FILE_2))
df3 = pd.read_csv(os.path.join(RAW_DIR, FILE_3))

print(f"Dataset 1: {len(df1)} rows")
print(f"Dataset 2: {len(df2)} rows")
print(f"Dataset 3: {len(df3)} rows")


# ============================================================
# STANDARDIZE COLUMNS
# ============================================================

BASE_COLUMNS = [
    "subject",
    "body",
    "answer",
    "type",
    "queue",
    "priority",
    "language",
    "version",
    "business_type",
]

TAG_COLUMNS = [
    "tag_1",
    "tag_2",
    "tag_3",
    "tag_4",
    "tag_5",
    "tag_6",
    "tag_7",
    "tag_8",
    "tag_9",
]


def standardize(df):
    df = df.copy()

    # Add missing standard columns
    for col in BASE_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    for col in TAG_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    # Keep only required columns
    return df[BASE_COLUMNS + TAG_COLUMNS]


df1 = standardize(df1)
df2 = standardize(df2)
df3 = standardize(df3)


# ============================================================
# NORMALIZE TEXT
# ============================================================

for df in [df1, df2, df3]:
    for col in BASE_COLUMNS + TAG_COLUMNS:
        df[col] = df[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )


# ============================================================
# REMOVE CROSS-DATASET DUPLICATES
# ============================================================

print("\n" + "=" * 80)
print("REMOVING DUPLICATES")
print("=" * 80)

duplicate_keys = [
    "subject",
    "body",
    "answer",
]

before_1 = len(df1)
before_2 = len(df2)

# Create a key containing records from Dataset 1
existing_keys = set(
    zip(
        df1["subject"].fillna(""),
        df1["body"].fillna(""),
        df1["answer"].fillna(""),
    )
)

# Keep only Dataset 2 records not already present in Dataset 1
df2_keys = list(
    zip(
        df2["subject"].fillna(""),
        df2["body"].fillna(""),
        df2["answer"].fillna(""),
    )
)

duplicate_mask = [
    key in existing_keys
    for key in df2_keys
]

duplicate_count = sum(duplicate_mask)

df2 = df2.loc[~pd.Series(duplicate_mask, index=df2.index)].copy()

print(f"Dataset 1 rows: {before_1}")
print(f"Dataset 2 rows before: {before_2}")
print(f"Duplicates removed from Dataset 2: {duplicate_count}")
print(f"Dataset 2 rows after: {len(df2)}")


# ============================================================
# COMBINE DATASETS
# ============================================================

combined = pd.concat(
    [df1, df2, df3],
    ignore_index=True
)

print("\nCombined rows:", len(combined))


# ============================================================
# REMOVE COMPLETELY EMPTY TAG COLUMNS
# ============================================================

for col in TAG_COLUMNS:
    if combined[col].isna().all():
        print(f"Removing completely empty column: {col}")
        combined.drop(columns=[col], inplace=True)


# ============================================================
# CREATE TICKET ID
# ============================================================

combined.insert(
    0,
    "ticket_id",
    range(1, len(combined) + 1)
)


# ============================================================
# CLEAN EMPTY STRINGS
# ============================================================

for col in combined.columns:
    if combined[col].dtype == "object":
        combined[col] = combined[col].replace(
            r"^\s*$",
            pd.NA,
            regex=True
        )


# ============================================================
# CREATE IT_TICKETS
# ============================================================

ticket_columns = [
    "ticket_id",
    "subject",
    "body",
    "answer",
    "type",
    "queue",
    "priority",
    "language",
    "version",
    "business_type",
]

it_tickets = combined[ticket_columns].copy()


# ============================================================
# CREATE IT_TAGS
# ============================================================

available_tag_columns = [
    col
    for col in TAG_COLUMNS
    if col in combined.columns
]

tags = combined[
    ["ticket_id"] + available_tag_columns
].melt(
    id_vars=["ticket_id"],
    value_vars=available_tag_columns,
    var_name="tag_position",
    value_name="tag"
)

# Remove empty tags
tags = tags.dropna(subset=["tag"])

tags["tag"] = tags["tag"].astype(str).str.strip()

tags = tags[tags["tag"] != ""]

# Keep only required columns
it_tags = tags[
    ["ticket_id", "tag"]
].copy()

# Remove exact duplicate ticket/tag combinations
it_tags = it_tags.drop_duplicates(
    subset=["ticket_id", "tag"]
)

# Sort
it_tags = it_tags.sort_values(
    ["ticket_id", "tag"]
).reset_index(drop=True)


# ============================================================
# SAVE PROCESSED DATA
# ============================================================

tickets_path = os.path.join(
    PROCESSED_DIR,
    "it_tickets.csv"
)

tags_path = os.path.join(
    PROCESSED_DIR,
    "it_tags.csv"
)

it_tickets.to_csv(
    tickets_path,
    index=False
)

it_tags.to_csv(
    tags_path,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("IT CLEANING COMPLETE")
print("=" * 80)

print(f"Final tickets: {len(it_tickets)}")
print(f"Final tags: {len(it_tags)}")

print("\nMissing values in it_tickets:")
print(it_tickets.isna().sum())

print("\nTag counts:")
print(it_tags["tag"].value_counts().head(20))

print("\nSaved:")
print(tickets_path)
print(tags_path)