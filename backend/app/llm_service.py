import os

from dotenv import load_dotenv
from groq import Groq

from backend.app.schema_service import get_domain_schema


load_dotenv("backend/.env")


api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set")


client = Groq(api_key=api_key)


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


def generate_sql(question: str, domain: str):
    schema = get_domain_schema(domain)
    schema_text = format_schema(schema)

    prompt = f"""
You are a Text-to-SQL system.

Convert the user's natural-language question into a PostgreSQL SQL query.

SELECTED DATABASE DOMAIN:
{domain}

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

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    sql = response.choices[0].message.content.strip()

    return sql