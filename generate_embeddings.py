"""
Generate embeddings for laws in the database
"""

import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def generate_embeddings():
    """Generate embeddings for all laws without embeddings"""

    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_anon_key = os.environ.get('SUPABASE_ANON_KEY')
    openai_api_key = os.environ.get('OPENAI_API_KEY')

    if not all([supabase_url, supabase_anon_key, openai_api_key]):
        print("❌ Missing environment variables")
        return

    print("=" * 80)
    print("Generating Embeddings for Saudi Laws")
    print("=" * 80)

    # Get all laws from database
    supabase = create_client(supabase_url, supabase_anon_key)

    try:
        # For now, directly insert embeddings using OpenAI API
        laws_result = supabase.table('laws').select('id, name_ar, name_en, full_text_ar, law_number').execute()
        laws = laws_result.data

        print(f"\n📊 Found {len(laws)} laws")

        for i, law in enumerate(laws, 1):
            print(f"\n[{i}/{len(laws)}] Processing: {law['name_en']}")

            # Generate embedding for the full text
            text_to_embed = f"{law['name_ar']}\n{law['full_text_ar']}"

            try:
                # Call OpenAI embeddings API
                response = requests.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "text-embedding-3-small",
                        "input": text_to_embed,
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    embedding_data = response.json()
                    embedding = embedding_data['data'][0]['embedding']

                    # Insert embedding into database
                    embedding_result = supabase.table('law_embeddings').insert({
                        'law_id': law['id'],
                        'text_chunk': text_to_embed[:1000],  # Store first 1000 chars
                        'embedding': embedding,
                        'chunk_index': 0
                    }).execute()

                    print(f"  ✅ Generated embedding for {law['name_en']}")
                else:
                    print(f"  ❌ Error: {response.status_code} - {response.text}")

            except Exception as e:
                print(f"  ❌ Error generating embedding: {e}")

        print("\n" + "=" * 80)
        print("✅ Embedding generation complete!")
        print("=" * 80)

        # Check total embeddings
        embeddings_count = supabase.table('law_embeddings').select('id', count='exact').execute()
        print(f"\n📊 Total embeddings in database: {embeddings_count.count}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    generate_embeddings()
