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

    # Remove one trailing semicolon
    if sql.endswith(";"):
        sql = sql[:-1].strip()

    # Prevent multiple SQL statements
    if ";" in sql:
        return {
            "valid": False,
            "reason": "Multiple SQL statements are not allowed.",
        }

    # Only SELECT queries are allowed
    if not re.match(r"^SELECT\b", sql, re.IGNORECASE):
        return {
            "valid": False,
            "reason": "Only SELECT queries are allowed.",
        }

    # Block dangerous SQL keywords
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

    # Check that the query uses an allowed schema
    schema_references = re.findall(
        r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\.",
        sql,
    )

    for schema_name in schema_references:
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