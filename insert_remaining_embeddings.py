#!/usr/bin/env python3
"""Add embeddings for existing laws"""

import time
from openai import OpenAI

env = {}
with open('.env') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            env[key] = val

openai_client = OpenAI(api_key=env['OPENAI_API_KEY'])

# Get existing laws without embeddings from database
EXISTING_LAWS = [
    {
        "id": "check_db",
        "name_ar": "النظام الأساسي للحكم",
        "text": "النظام الأساسي للحكم: المملكة العربية السعودية، دولة عربية إسلامية، ذات سيادة تامة، دينها الإسلام، ودستورها كتاب الله تعالى وسنة رسوله."
    },
    {
        "id": "check_db2",
        "name_ar": "نظام مكافحة جرائم الإرهاب وتمويله",
        "text": "نظام مكافحة جرائم الإرهاب وتمويله: يهدف هذا النظام إلى مكافحة الإرهاب وتمويله وحماية المجتمع والأفراد من الأعمال الإرهابية."
    }
]

print("🧠 Generating embeddings for existing laws...")

for law in EXISTING_LAWS:
    print(f"\n📜 {law['name_ar']}")
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=f"{law['name_ar']}\n\n{law['text']}"
        )
        embedding = response.data[0].embedding
        print(f"   ✅ Embedding generated ({len(embedding)} dimensions)")
        
        # Output SQL
        print(f"\n   SQL to execute:")
        print(f"   UPDATE law_embeddings SET embedding = '{embedding}'::vector")
        print(f"   WHERE law_id = (SELECT id FROM laws WHERE name_ar = '{law['name_ar']}');")
        
        time.sleep(1)
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n✅ Done! Copy SQL statements above to Supabase SQL Editor")
