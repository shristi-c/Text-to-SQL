def generate_answer(question: str, result: dict):
    columns = result.get("columns", [])
    rows = result.get("rows", [])
    row_count = result.get("row_count", 0)

    # No results
    if row_count == 0:
        return "No matching records were found."

    # Single value result
    if len(rows) == 1 and len(columns) == 1:
        value = rows[0][0]

        if value is None:
            return "The query returned no value."

        return f"The answer is {value}."

    # Single row with multiple columns
    if len(rows) == 1:
        values = rows[0]

        parts = [
            f"{column}: {value}"
            for column, value in zip(columns, values)
        ]

        return "The result is: " + ", ".join(parts) + "."

    # Multiple rows
    if len(columns) == 1:
        values = [row[0] for row in rows]

        return (
            f"The query returned {row_count} records. "
            f"The values are: {', '.join(str(value) for value in values)}."
        )

    # Multiple rows and multiple columns
    return f"The query returned {row_count} records."