from typing import List, Dict, Any
import psycopg2
from psycopg2 import sql

# --- Helper to convert psycopg2 rows to dictionaries ---
def row_to_dict(cursor, row):
    """Converts a psycopg2 row to a dictionary using cursor.description."""
    if row is None:
        return None
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}

# --- Analytical Query Functions ---

def get_top_products(db_conn: psycopg2.extensions.connection, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Returns the most frequently mentioned "products" (keywords) from messages.
    """
    product_keywords = [
        'paracetamol', 'ibuprofen', 'amoxicillin', 'vaccine', 'tablet', 'syrup',
        'cream', 'mask', 'sanitizer', 'antibiotic', 'antiviral', 'diagnostic',
        'test kit', 'ventilator', 'medicine', 'drug', 'injection', 'pill'
    ]

    keyword_conditions = [sql.SQL("message_text ILIKE %s") for _ in product_keywords]
    where_clause = sql.SQL(" OR ").join(keyword_conditions)

    query = sql.SQL("""
        WITH keyword_mentions AS (
            SELECT
                message_id,
                message_text,
                unnest(ARRAY[{keywords}]) AS detected_keyword
            FROM
                public.fct_messages -- <--- CHANGED TO public
            WHERE
                {where_clause}
        )
        SELECT
            detected_keyword AS product_name,
            COUNT(*) AS mention_count
        FROM
            keyword_mentions
        GROUP BY
            detected_keyword
        ORDER BY
            mention_count DESC
        LIMIT %s;
    """).format(
        keywords=sql.SQL(",").join(sql.Literal(k) for k in product_keywords),
        where_clause=where_clause
    )

    with db_conn.cursor() as cur:
        cur.execute(query, product_keywords + [limit])
        results = [row_to_dict(cur, row) for row in cur.fetchall()]
    return results

def get_channel_activity(db_conn: psycopg2.extensions.connection, channel_name: str) -> List[Dict[str, Any]]:
    """
    Returns the posting activity (message count per day) for a specific channel.
    """
    query = sql.SQL("""
        SELECT
            dd.full_date::text AS date,
            COUNT(fm.message_id) AS message_count
        FROM
            public.fct_messages fm -- <--- CHANGED TO public
        JOIN
            public.dim_channels dc ON fm.channel_id = dc.channel_id -- <--- CHANGED TO public
        JOIN
            public.dim_dates dd ON fm.date_key = dd.date_key -- <--- CHANGED TO public
        WHERE
            dc.channel_name ILIKE %s
        GROUP BY
            dd.full_date
        ORDER BY
            dd.full_date;
    """)

    with db_conn.cursor() as cur:
        cur.execute(query, (channel_name,))
        results = [row_to_dict(cur, row) for row in cur.fetchall()]
    return results

def search_messages(db_conn: psycopg2.extensions.connection, query_text: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Searches for messages containing a specific keyword in their text.
    """
    search_pattern = f"%{query_text}%"

    query = sql.SQL("""
        SELECT
            fm.message_id,
            dc.channel_name,
            fm.message_date,
            fm.message_text,
            fm.has_media,
            fm.media_type
        FROM
            public.fct_messages fm -- <--- CHANGED TO public
        JOIN
            public.dim_channels dc ON fm.channel_id = dc.channel_id -- <--- CHANGED TO public
        WHERE
            fm.message_text ILIKE %s
        ORDER BY
            fm.message_date DESC
        LIMIT %s;
    """)

    with db_conn.cursor() as cur:
        cur.execute(query, (search_pattern, limit))
        results = [row_to_dict(cur, row) for row in cur.fetchall()]
    return results

