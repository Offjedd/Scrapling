#!/usr/bin/env python3
"""Generate embeddings using HTTP requests"""
import os
import requests
import time
from openai import OpenAI

# Load env
env = {}
with open('.env') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            env[key] = val

SUPABASE_URL = env['SUPABASE_URL']
SERVICE_KEY = env['SUPABASE_SERVICE_ROLE_KEY']
OPENAI_KEY = env['OPENAI_API_KEY']

headers = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json'
}

openai_client = OpenAI(api_key=OPENAI_KEY)

print("=" * 80)
print("🧠 Generating Embeddings via REST API")
print("=" * 80)

# Get all laws
laws_resp = requests.get(f'{SUPABASE_URL}/rest/v1/laws', headers=headers)
laws = laws_resp.json()
print(f"\n📊 Found {len(laws)} laws")

# Get existing embeddings
emb_resp = requests.get(f'{SUPABASE_URL}/rest/v1/law_embeddings?select=law_id', headers=headers)
existing = {e['law_id'] for e in emb_resp.json()}
print(f"✅ {len(existing)} already have embeddings\n")

added = 0

for law in laws:
    if law['id'] in existing:
        print(f"⏭️  {law['name_ar']}")
        continue
    
    print(f"📜 {law['name_ar']}")
    
    try:
        text = f"{law['name_ar']}\n\n{law.get('full_text_ar', '')}"
        
        # Generate embedding
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]
        )
        embedding = response.data[0].embedding
        
        # Insert
        insert_resp = requests.post(
            f'{SUPABASE_URL}/rest/v1/law_embeddings',
            headers=headers,
            json={
                'law_id': law['id'],
                'text_chunk': law['name_ar'],
                'embedding': embedding,
                'chunk_index': 0
            }
        )
        
        if insert_resp.status_code in [200, 201]:
            print(f"   ✅ Embedding added!")
            added += 1
        else:
            print(f"   ❌ HTTP {insert_resp.status_code}: {insert_resp.text[:100]}")
        
        time.sleep(0.5)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print(f"✅ Complete! Added {added} embeddings")
print("=" * 80)
