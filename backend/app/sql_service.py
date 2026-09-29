from sqlalchemy import text

from backend.app.database import engine


MAX_ROWS = 100


def execute_sql(sql: str):
    sql = sql.strip().rstrip(";")

    # Add a row limit if the query does not already have one.
    if "LIMIT" not in sql.upper():
        sql = f"{sql} LIMIT {MAX_ROWS}"

    with engine.connect() as connection:
        result = connection.execute(text(sql))

        columns = list(result.keys())
        rows = result.fetchall()

    return {
        "columns": columns,
        "rows": [list(row) for row in rows],
        "row_count": len(rows),
    }