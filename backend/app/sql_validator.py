import re


FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "EXECUTE",
    "CALL",
}


ALLOWED_SCHEMAS = {
    "it",
    "retail",
    "airline",
}


def validate_sql(sql: str):
    if not sql or not sql.strip():
        return {
            "valid": False,
            "reason": "SQL query is empty.",
        }

    sql = sql.strip()

    if sql.endswith(";"):
        sql = sql[:-1].strip()

    if ";" in sql:
        return {
            "valid": False,
            "reason": "Multiple SQL statements are not allowed.",
        }

    if not re.match(r"^SELECT\b", sql, re.IGNORECASE):
        return {
            "valid": False,
            "reason": "Only SELECT queries are allowed.",
        }

    words = set(
        re.findall(r"\b[A-Z_]+\b", sql.upper())
    )

    forbidden_found = words.intersection(FORBIDDEN_KEYWORDS)

    if forbidden_found:
        return {
            "valid": False,
            "reason": (
                "Forbidden SQL operation detected: "
                + ", ".join(sorted(forbidden_found))
            ),
        }

    # Check schema-qualified table references that appear
    # after FROM or JOIN.
    #
    # This allows table aliases such as:
    #   SELECT p.name FROM retail.products p
    #
    # while still rejecting unauthorized schemas such as:
    #   SELECT * FROM public.users
    schema_references = re.findall(
        r"\b(FROM|JOIN)\s+"
        r"([a-zA-Z_][a-zA-Z0-9_]*)\."
        r"([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        re.IGNORECASE,
    )

    for _, schema_name, table_name in schema_references:
        if schema_name.lower() not in ALLOWED_SCHEMAS:
            return {
                "valid": False,
                "reason": (
                    f"Schema '{schema_name}' is not allowed."
                ),
            }

    return {
        "valid": True,
        "reason": "SQL query passed validation.",
    }