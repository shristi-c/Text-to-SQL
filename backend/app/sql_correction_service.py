import os

from dotenv import load_dotenv
from groq import Groq

from backend.app.schema_service import get_domain_schema
from backend.app.llm_service import format_schema


load_dotenv("backend/.env")


api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set")


client = Groq(api_key=api_key)


def correct_sql(
    question: str,
    domain: str,
    failed_sql: str,
    error_message: str,
):
    schema = get_domain_schema(domain)
    schema_text = format_schema(schema)

    prompt = f"""
You are a PostgreSQL Text-to-SQL correction system.

The original user question was:

{question}

SELECTED DATABASE DOMAIN:
{domain}

DATABASE SCHEMA:
{schema_text}

The previously generated SQL query failed.

FAILED SQL:
{failed_sql}

DATABASE ERROR:
{error_message}

Generate a corrected PostgreSQL SQL query that answers the original user question.

RULES:
- Generate only SELECT queries.
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, GRANT, REVOKE, EXECUTE, or CALL.
- Use only tables and columns that exist in the provided schema.
- Always use the correct schema-qualified table names.
- Do not invent tables or columns.
- Fix the SQL based on the database error.
- Do not use markdown code fences.
- Return only the corrected SQL query.
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

    corrected_sql = response.choices[0].message.content.strip()

    return corrected_sql