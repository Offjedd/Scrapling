"""
Insert embeddings directly into Supabase using service role
"""

import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def insert_embeddings():
    """Generate and insert embeddings for all laws"""

    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    openai_key = os.environ.get('OPENAI_API_KEY')

    if not all([supabase_url, supabase_service_key, openai_key]):
        print("❌ Missing environment variables")
        return

    # Use service role to bypass RLS
    supabase = create_client(supabase_url, supabase_service_key)

    print("=" * 80)
    print("Generating and Inserting Embeddings")
    print("=" * 80)

    # Get all laws from database
    try:
        laws_result = supabase.table('laws').select('id, name_ar, full_text_ar').execute()
        laws = laws_result.data

        print(f"\n📊 Found {len(laws)} laws")

        for i, law in enumerate(laws, 1):
            print(f"\n[{i}/{len(laws)}] Processing law: {law['name_ar']}")

            # Prepare text for embedding
            text = f"{law['name_ar']}\n{law['full_text_ar']}"

            try:
                # Generate embedding
                response = requests.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {openai_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "text-embedding-3-small",
                        "input": text,
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    embedding_data = response.json()
                    embedding = embedding_data['data'][0]['embedding']

                    # Insert via RPC or raw SQL to bypass RLS
                    # First, let's try using execute SQL
                    from supabase import PostgrestAPIError

                    # Try direct insert with service role
                    insert_result = supabase.table('law_embeddings').insert({
                        'law_id': law['id'],
                        'text_chunk': text[:1000],
                        'embedding': embedding,
                        'chunk_index': 0
                    }).execute()

                    print(f"  ✅ Inserted embedding (ID: {insert_result.data[0]['id'][:8]}...)")

                else:
                    print(f"  ❌ OpenAI Error: {response.status_code}")

            except Exception as e:
                print(f"  ❌ Error: {e}")

        print("\n" + "=" * 80)
        print("✅ Embedding insertion complete!")
        print("=" * 80)

        # Check count
        count = supabase.table('law_embeddings').select('id', count='exact').execute()
        print(f"\n📊 Total embeddings: {count.count}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    insert_embeddings()
