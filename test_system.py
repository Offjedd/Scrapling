"""
Test the Saudi Law AI Assistant system
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_query_function():
    """Test the query-law edge function"""

    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_anon_key = os.environ.get('SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_anon_key:
        print("❌ Missing environment variables")
        return

    # Test URL
    function_url = f"{supabase_url}/functions/v1/query-law"

    # Test questions in Arabic
    test_questions = [
        "ما هي ساعات العمل القانونية في السعودية؟",
        "ما هو النظام الأساسي للحكم؟",
        "ماذا يقول القانون عن الإجازة السنوية؟"
    ]

    print("=" * 80)
    print("Testing Saudi Law AI Assistant")
    print("=" * 80)

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {question}")
        print('='*80)

        try:
            response = requests.post(
                function_url,
                headers={
                    'Authorization': f'Bearer {supabase_anon_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'question': question,
                    'language': 'ar',
                    'max_results': 3
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Success!")
                print(f"\n📝 Answer:")
                print(data.get('answer', 'No answer'))
                print(f"\n📚 Citations: {len(data.get('citations', []))}")
                for citation in data.get('citations', []):
                    print(f"  - {citation.get('law_name_ar')} (المادة {citation.get('article_number')})")
                print(f"\n⏱️  Response time: {data.get('response_time_ms')}ms")
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)

        except Exception as e:
            print(f"❌ Exception: {e}")

    print("\n" + "=" * 80)
    print("Testing complete!")
    print("=" * 80)


def check_database():
    """Check the database content"""
    from supabase import create_client

    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Missing credentials")
        return

    supabase = create_client(supabase_url, supabase_key)

    print("\n" + "=" * 80)
    print("Database Status")
    print("=" * 80)

    try:
        # Count laws
        result = supabase.table('laws').select('id', count='exact').execute()
        print(f"\n📊 Total laws: {result.count}")

        # Get law names
        laws = supabase.table('laws').select('name_ar, name_en, law_number').execute()
        print(f"\n📚 Laws in database:")
        for law in laws.data:
            print(f"  - {law['name_en']} ({law['law_number']})")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    check_database()
    print("\n")
    test_query_function()
