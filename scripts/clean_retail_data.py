import pandas as pd
from pathlib import Path


RAW_FILE = Path("data/raw/retail/Retail-Supply-Chain-Sales-Dataset.xlsx")
OUTPUT_DIR = Path("data/processed/retail")


def main():
    print("=" * 80)
    print("RETAIL DATA CLEANING")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. READ DATA
    # ------------------------------------------------------------------
    df = pd.read_excel(
        RAW_FILE,
        sheet_name="Retails Order Full Dataset"
    )

    print(f"Original rows: {len(df)}")
    print(f"Original columns: {len(df.columns)}")

    # ------------------------------------------------------------------
    # 2. CLEAN COLUMN NAMES
    # ------------------------------------------------------------------
    df.columns = df.columns.str.strip()

    string_columns = [
        "Order ID",
        "Ship Mode",
        "Customer ID",
        "Customer Name",
        "Segment",
        "Country",
        "City",
        "State",
        "Region",
        "Retail Sales People",
        "Product ID",
        "Category",
        "Sub-Category",
        "Product Name",
        "Returned"
    ]

    for col in string_columns:
        df[col] = df[col].astype("string").str.strip()

    # ------------------------------------------------------------------
    # 3. DATE COLUMNS
    # ------------------------------------------------------------------
    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        errors="coerce"
    )

    df["Ship Date"] = pd.to_datetime(
        df["Ship Date"],
        errors="coerce"
    )

    # ------------------------------------------------------------------
    # 4. PRODUCT VALIDATION
    # ------------------------------------------------------------------
    product_pairs = (
        df[
            [
                "Product ID",
                "Product Name",
                "Category",
                "Sub-Category"
            ]
        ]
        .drop_duplicates()
        .sort_values(["Product ID", "Product Name"])
    )

    product_id_counts = (
        product_pairs.groupby("Product ID")
        .size()
    )

    inconsistent_products = product_id_counts[
        product_id_counts > 1
    ]

    print()
    print("=" * 80)
    print("PRODUCT VALIDATION")
    print("=" * 80)

    print(
        f"Unique Product IDs: {df['Product ID'].nunique()}"
    )

    print(
        f"Unique Product ID + Product Name combinations: "
        f"{len(product_pairs)}"
    )

    print(
        f"Product IDs with multiple names: "
        f"{len(inconsistent_products)}"
    )

    if len(inconsistent_products) > 0:
        print(
            "Source data contains multiple names for some Product IDs."
        )
        print(
            "Keeping each Product ID + Product Name combination "
            "as a separate product record."
        )

    # ------------------------------------------------------------------
    # 5. CREATE PRODUCT TABLE
    # ------------------------------------------------------------------
    products = product_pairs.copy()

    products.insert(
        0,
        "product_key",
        range(1, len(products) + 1)
    )

    products = products.rename(
        columns={
            "Product ID": "product_id",
            "Product Name": "product_name",
            "Category": "category",
            "Sub-Category": "sub_category"
        }
    )

    # Create lookup for exact Product ID + Product Name combination
    product_lookup = (
        products[
            [
                "product_key",
                "product_id",
                "product_name"
            ]
        ]
        .copy()
    )

    # ------------------------------------------------------------------
    # 6. CREATE CUSTOMERS
    # ------------------------------------------------------------------
    customers = (
        df[
            [
                "Customer ID",
                "Customer Name",
                "Segment"
            ]
        ]
        .drop_duplicates("Customer ID")
        .rename(
            columns={
                "Customer ID": "customer_id",
                "Customer Name": "customer_name",
                "Segment": "segment"
            }
        )
        .sort_values("customer_id")
    )

    customers = customers.reset_index(drop=True)

    # ------------------------------------------------------------------
    # 7. CREATE ORDERS
    # ------------------------------------------------------------------
    orders = (
        df[
            [
                "Order ID",
                "Order Date",
                "Ship Date",
                "Ship Mode",
                "Customer ID",
                "Country",
                "City",
                "State",
                "Postal Code",
                "Region",
                "Retail Sales People"
            ]
        ]
        .drop_duplicates("Order ID")
        .rename(
            columns={
                "Order ID": "order_id",
                "Order Date": "order_date",
                "Ship Date": "ship_date",
                "Ship Mode": "ship_mode",
                "Customer ID": "customer_id",
                "Country": "country",
                "City": "city",
                "State": "state",
                "Postal Code": "postal_code",
                "Region": "region",
                "Retail Sales People": "retail_sales_person"
            }
        )
        .sort_values("order_id")
    )

    orders = orders.reset_index(drop=True)

    # ------------------------------------------------------------------
    # 8. CREATE ORDER ITEMS
    # ------------------------------------------------------------------
    order_items = df[
        [
            "Row ID",
            "Order ID",
            "Product ID",
            "Product Name",
            "Returned",
            "Sales",
            "Quantity",
            "Discount",
            "Profit"
        ]
    ].copy()

    # Match every order item to the exact product record
    order_items = order_items.merge(
        product_lookup,
        left_on=["Product ID", "Product Name"],
        right_on=["product_id", "product_name"],
        how="left",
        validate="many_to_one"
    )

    order_items = order_items[
        [
            "Row ID",
            "Order ID",
            "product_key",
            "Returned",
            "Sales",
            "Quantity",
            "Discount",
            "Profit"
        ]
    ]

    order_items = order_items.rename(
        columns={
            "Row ID": "row_id",
            "Order ID": "order_id",
            "Returned": "returned",
            "Sales": "sales",
            "Quantity": "quantity",
            "Discount": "discount",
            "Profit": "profit"
        }
    )

    order_items = order_items.sort_values("row_id")
    order_items = order_items.reset_index(drop=True)

    # ------------------------------------------------------------------
    # 9. VALIDATION
    # ------------------------------------------------------------------
    invalid_product_keys = (
        ~order_items["product_key"].isin(
            products["product_key"]
        )
    ).sum()

    invalid_customer_ids = (
        ~orders["customer_id"].isin(
            customers["customer_id"]
        )
    ).sum()

    print()
    print("=" * 80)
    print("REFERENTIAL INTEGRITY CHECK")
    print("=" * 80)

    print(
        f"Order items with invalid product_key: "
        f"{invalid_product_keys}"
    )

    print(
        f"Orders with invalid customer_id: "
        f"{invalid_customer_ids}"
    )

    # ------------------------------------------------------------------
    # 10. SAVE
    # ------------------------------------------------------------------
    customers.to_csv(
        OUTPUT_DIR / "customers.csv",
        index=False
    )

    products.to_csv(
        OUTPUT_DIR / "products.csv",
        index=False
    )

    orders.to_csv(
        OUTPUT_DIR / "orders.csv",
        index=False
    )

    order_items.to_csv(
        OUTPUT_DIR / "order_items.csv",
        index=False
    )

    # ------------------------------------------------------------------
    # 11. SUMMARY
    # ------------------------------------------------------------------
    print()
    print("=" * 80)
    print("RETAIL CLEANING COMPLETE")
    print("=" * 80)

    print(f"Customers:   {len(customers)}")
    print(f"Products:    {len(products)}")
    print(f"Orders:      {len(orders)}")
    print(f"Order Items: {len(order_items)}")

    print()
    print("Saved:")
    print(OUTPUT_DIR / "customers.csv")
    print(OUTPUT_DIR / "products.csv")
    print(OUTPUT_DIR / "orders.csv")
    print(OUTPUT_DIR / "order_items.csv")


if __name__ == "__main__":
    main()