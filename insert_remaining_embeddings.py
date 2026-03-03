#!/usr/bin/env python3
"""
Insert remaining embeddings using direct database connection
"""

import os
import psycopg2

def insert_embeddings():
    """Insert embeddings via PostgreSQL connection"""

    # Read database URL from .env file
    with open('.env') as f:
        for line in f:
            if line.startswith('SUPABASE_DB_URL='):
                db_url = line.split('=', 1)[1].strip()
                break
        else:
            db_url = None

    if not db_url:
        print("❌ Missing SUPABASE_DB_URL")
        return

    print("=" * 80)
    print("Inserting Remaining Embeddings")
    print("=" * 80)

    # Connect to database
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    # Read embedding files
    embeddings_to_insert = [
        ('04156ed9-d15d-414d-b1b4-62e7a88adc31', 'emb_04156ed9.txt', 'النظام الأساسي للحكم'),
        ('961ad019-c689-495f-aa88-dfc9bae982e4', 'emb_961ad019.txt', 'نظام مكافحة جرائم الإرهاب'),
    ]

    for law_id, filename, text_chunk in embeddings_to_insert:
        print(f"\n📖 Inserting: {text_chunk}")

        try:
            # Read embedding
            with open(filename) as f:
                embedding_str = f.read().strip()

            # Insert using parameterized query
            cursor.execute(
                """
                INSERT INTO law_embeddings (law_id, text_chunk, embedding, chunk_index)
                VALUES (%s, %s, %s::vector, 0)
                RETURNING id
                """,
                (law_id, text_chunk, embedding_str)
            )

            result = cursor.fetchone()
            conn.commit()

            print(f"  ✅ Inserted! ID: {result[0]}")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            conn.rollback()

    # Check total count
    cursor.execute("SELECT COUNT(*) FROM law_embeddings")
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print("\n" + "=" * 80)
    print(f"✅ Complete! Total embeddings: {count}")
    print("=" * 80)

if __name__ == "__main__":
    insert_embeddings()
