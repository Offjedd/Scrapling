#!/usr/bin/env python3
"""Generate embeddings for all laws without them"""
import os
from openai import OpenAI
from supabase import create_client
import time

# Load env
env = {}
with open('.env') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            env[key] = val

# Initialize clients
supabase = create_client(env['SUPABASE_URL'], env['SUPABASE_SERVICE_ROLE_KEY'])
openai_client = OpenAI(api_key=env['OPENAI_API_KEY'])

print("=" * 80)
print("🧠 Generating Embeddings for All Laws")
print("=" * 80)

# Get all laws
laws_response = supabase.table('laws').select('*').execute()
laws = laws_response.data

print(f"\n📊 Found {len(laws)} laws in database")

# Get laws that already have embeddings
embeddings_response = supabase.table('law_embeddings').select('law_id').execute()
laws_with_embeddings = {emb['law_id'] for emb in embeddings_response.data}

print(f"✅ {len(laws_with_embeddings)} laws already have embeddings")

# Process laws without embeddings
added_count = 0

for law in laws:
    law_id = law['id']
    
    if law_id in laws_with_embeddings:
        print(f"\n⏭️  {law['name_ar']} - Already has embedding")
        continue
    
    print(f"\n📜 {law['name_ar']}")
    
    try:
        # Generate embedding
        text_for_embedding = f"{law['name_ar']}\n\n{law.get('full_text_ar', '')}"
        
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text_for_embedding[:8000]
        )
        embedding = response.data[0].embedding
        
        # Insert embedding
        supabase.table('law_embeddings').insert({
            'law_id': law_id,
            'text_chunk': law['name_ar'],
            'embedding': embedding,
            'chunk_index': 0
        }).execute()
        
        print(f"   ✅ Embedding added!")
        added_count += 1
        
        time.sleep(0.5)  # Rate limiting
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print(f"✅ Complete! Added {added_count} new embeddings")
print("=" * 80)

# Final count
final_embeddings = supabase.table('law_embeddings').select('id').execute()
final_laws = supabase.table('laws').select('id').execute()

print(f"\n📊 Final Status:")
print(f"   Total Laws: {len(final_laws.data)}")
print(f"   Laws with Embeddings: {len(final_embeddings.data)}")
print(f"\n🎉 Your AI is ready to answer questions!")
