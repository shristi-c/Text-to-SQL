import os

from dotenv import load_dotenv
from google import genai

from backend.app.schema_service import get_database_schema


load_dotenv("backend/.env")

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set")


client = genai.Client(api_key=api_key)


def format_schema(schema):
    lines = []

    for schema_name, tables in schema.items():
        lines.append(f"SCHEMA: {schema_name}")

        for table_name, columns in tables.items():
            column_names = ", ".join(
                column["name"] for column in columns
            )

            lines.append(
                f"TABLE: {schema_name}.{table_name} "
                f"({column_names})"
            )

    return "\n".join(lines)


def generate_sql(question: str):
    schema = get_database_schema()
    schema_text = format_schema(schema)

    prompt = f"""
You are a Text-to-SQL system.

Convert the user's natural-language question into a PostgreSQL SQL query.

DATABASE SCHEMA:
{schema_text}

RULES:
- Generate only SELECT queries.
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, GRANT, REVOKE, EXECUTE, or CALL.
- Use only tables and columns that exist in the provided schema.
- Always use the correct schema-qualified table name.
- Do not invent tables or columns.
- Do not use markdown code fences.
- Return only the SQL query.
- Do not include explanations.

USER QUESTION:
{question}
"""

    interaction = client.interactions.create(
       model=model,
        input=prompt,
    )

    sql = interaction.output_text.strip()

    return sql