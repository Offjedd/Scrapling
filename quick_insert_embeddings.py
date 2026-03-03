#!/usr/bin/env python3
"""
Quick script to insert remaining embeddings via SQL
"""

import subprocess

# Embeddings to insert
embeddings = [
    ('04156ed9-d15d-414d-b1b4-62e7a88adc31', 'emb_04156ed9.txt', 'النظام الأساسي للحكم'),
    ('961ad019-c689-495f-aa88-dfc9bae982e4', 'emb_961ad019.txt', 'نظام مكافحة جرائم الإرهاب'),
]

print("=" * 80)
print("Inserting Remaining Embeddings")
print("=" * 80)

for law_id, filename, text_chunk in embeddings:
    print(f"\n📖 Inserting: {text_chunk}")

    # Read embedding
    with open(f'/tmp/cc-agent/64271028/project/{filename}') as f:
        embedding = f.read().strip()

    # Create SQL
    sql = f"INSERT INTO law_embeddings (law_id, text_chunk, embedding, chunk_index) VALUES ('{law_id}', '{text_chunk}', '{embedding}'::vector, 0) RETURNING id;"

    # Write to temp file
    with open('/tmp/insert_temp.sql', 'w') as f:
        f.write(sql)

    print(f"  ✅ Embedding ready ({embedding.count(',') + 1} dimensions)")
    print(f"  ⚠️  Manual SQL execution required due to token limits")
    print(f"  📝 SQL saved to /tmp/insert_temp.sql")
    print(f"  🔧 Use: mcp__supabase__execute_sql with the SQL content")

print("\n" + "=" * 80)
print("✅ Embeddings prepared!")
print("=" * 80)
print("\nNext step: Execute the SQL via Supabase MCP tool")
