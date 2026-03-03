"""
Generate embeddings for laws using direct SQL (bypasses RLS)
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


def generate_embeddings():
    """Generate embeddings for all laws"""

    openai_key = os.environ.get('OPENAI_API_KEY')

    if not openai_key:
        print("❌ Missing OPENAI_API_KEY")
        return

    print("=" * 80)
    print("Generating Embeddings for Saudi Laws")
    print("=" * 80)

    # Sample laws data (we know these are already in the DB)
    laws = [
        {
            'id': '04156ed9-d15d-414d-b1b4-62e7a88adc31',
            'text': 'النظام الأساسي للحكم. المادة الأولى: المملكة العربية السعودية، دولة عربية إسلامية، ذات سيادة تامة؛ دينها الإسلام',
        },
        {
            'id': '961ad019-c689-495f-aa88-dfc9bae982e4',
            'text': 'نظام مكافحة جرائم الإرهاب وتمويله. المادة الأولى: تُقصد بالعبارات والألفاظ الآتية المعاني المُبينة. المادة الثانية: يُعاقب كل من يرتكب جريمة إرهابية',
        },
        {
            'id': '95a161ce-c963-400e-ad2a-25e178af2feb',
            'text': 'نظام العمل. المادة الأولى: يقصد بالألفاظ والعبارات الآتية المعاني الموضحة. المادة الثانية: يجب أن تكون ساعات العمل ثماني ساعات. المادة الثالثة: للعامل الحق في إجازة سنوية',
        },
    ]

    embeddings_sql = []

    for i, law in enumerate(laws, 1):
        print(f"\n[{i}/{len(laws)}] Generating embedding for law {law['id'][:8]}...")

        try:
            # Call OpenAI embeddings API
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "text-embedding-3-small",
                    "input": law['text'],
                },
                timeout=30
            )

            if response.status_code == 200:
                embedding_data = response.json()
                embedding = embedding_data['data'][0]['embedding']

                # Format embedding as PostgreSQL array
                embedding_str = '[' + ','.join(map(str, embedding)) + ']'

                embeddings_sql.append(
                    f"INSERT INTO law_embeddings (law_id, text_chunk, embedding, chunk_index) "
                    f"VALUES ('{law['id']}', '{law['text'][:500]}', '{embedding_str}'::vector, 0);"
                )

                print(f"  ✅ Generated embedding (dimension: {len(embedding)})")
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    # Save SQL file
    if embeddings_sql:
        sql_content = '\n'.join(embeddings_sql)
        with open('insert_embeddings.sql', 'w') as f:
            f.write(sql_content)

        print("\n" + "=" * 80)
        print("✅ SQL file generated: insert_embeddings.sql")
        print("=" * 80)
        print("\nYou can now insert embeddings using:")
        print("  1. Supabase SQL tool")
        print("  2. Or run: psql < insert_embeddings.sql")
        print("\nSQL preview:")
        print(embeddings_sql[0][:200] + "...")


if __name__ == "__main__":
    generate_embeddings()
