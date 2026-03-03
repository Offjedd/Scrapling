#!/usr/bin/env python3
"""
Insert embeddings via Supabase REST API
"""

import requests
import json

# Read env values
with open('.env') as f:
    env = {}
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            env[key] = val

supabase_url = env.get('SUPABASE_URL')
service_key = env.get('SUPABASE_SERVICE_ROLE_KEY')

print("=" * 80)
print("Inserting Embeddings via REST API")
print("=" * 80)

# Embeddings to insert
embeddings_data = [
    ('04156ed9-d15d-414d-b1b4-62e7a88adc31', 'emb_04156ed9.txt', 'النظام الأساسي للحكم'),
    ('961ad019-c689-495f-aa88-dfc9bae982e4', 'emb_961ad019.txt', 'نظام مكافحة جرائم الإرهاب'),
]

for law_id, filename, text_chunk in embeddings_data:
    print(f"\n📖 Processing: {text_chunk}")

    # Read embedding
    with open(filename) as f:
        embedding_str = f.read().strip()

    # Parse to list
    embedding_list = json.loads(embedding_str)

    print(f"  📊 Embedding dimensions: {len(embedding_list)}")

    # Insert via REST API
    response = requests.post(
        f"{supabase_url}/rest/v1/law_embeddings",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        json={
            "law_id": law_id,
            "text_chunk": text_chunk,
            "embedding": embedding_list,
            "chunk_index": 0
        },
        timeout=30
    )

    if response.status_code in [200, 201]:
        print(f"  ✅ Inserted successfully!")
    else:
        print(f"  ❌ Error {response.status_code}: {response.text[:200]}")

print("\n" + "=" * 80)
print("✅ Insertion complete!")
print("=" * 80)
