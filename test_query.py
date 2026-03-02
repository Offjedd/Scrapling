#!/usr/bin/env python3
"""
Quick test script for the Saudi Law AI Assistant
Tests the query-law API endpoint with sample questions
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://exilgibjcnrtashitzjk.supabase.co')
SUPABASE_ANON_KEY = os.getenv('VITE_SUPABASE_ANON_KEY', '')

# Sample questions in Arabic and English
SAMPLE_QUESTIONS = [
    {
        'question': 'ما هي حقوق الموظف عند إنهاء العقد؟',
        'language': 'ar',
        'description': 'Employee rights upon contract termination'
    },
    {
        'question': 'ماذا ينص نظام العمل عن ساعات العمل؟',
        'language': 'ar',
        'description': 'Working hours according to labor law'
    },
    {
        'question': 'What are the requirements for establishing a company in Saudi Arabia?',
        'language': 'en',
        'description': 'Company establishment requirements'
    },
    {
        'question': 'ما هي حقوق المستهلك؟',
        'language': 'ar',
        'description': 'Consumer rights'
    },
]


def test_query(question: str, language: str = 'ar', max_results: int = 5) -> dict:
    """Test the query-law API endpoint"""

    url = f"{SUPABASE_URL}/functions/v1/query-law"

    headers = {
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }

    payload = {
        'question': question,
        'language': language,
        'max_results': max_results
    }

    try:
        print(f"\n{'=' * 80}")
        print(f"Question: {question}")
        print(f"Language: {language}")
        print(f"{'=' * 80}\n")

        response = requests.post(url, headers=headers, json=payload, timeout=60)

        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None

        result = response.json()

        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return None

        # Display answer
        print("📝 Answer:")
        print("-" * 80)
        print(result.get('answer', 'No answer provided'))
        print("-" * 80)

        # Display citations
        citations = result.get('citations', [])
        if citations:
            print(f"\n📚 Citations ({len(citations)}):")
            for idx, citation in enumerate(citations, 1):
                print(f"\n{idx}. {citation.get('law_name_ar', 'N/A')}")
                print(f"   رقم النظام: {citation.get('law_number', 'N/A')}")
                print(f"   رقم المادة: {citation.get('article_number', 'N/A')}")
                print(f"   تاريخ النشر: {citation.get('publication_date', 'N/A')}")
                print(f"   الرابط: {citation.get('law_url', 'N/A')}")

        # Display stats
        response_time = result.get('response_time_ms', 0)
        print(f"\n⏱️  Response Time: {response_time}ms")

        return result

    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def run_all_tests():
    """Run all sample questions"""
    print("=" * 80)
    print("Saudi Law AI Assistant - API Test")
    print("=" * 80)

    if not SUPABASE_ANON_KEY:
        print("\n❌ Error: SUPABASE_ANON_KEY not found in environment variables")
        print("Please make sure .env file is configured correctly")
        return

    results = []

    for idx, sample in enumerate(SAMPLE_QUESTIONS, 1):
        print(f"\n\nTest {idx}/{len(SAMPLE_QUESTIONS)}: {sample['description']}")
        result = test_query(
            question=sample['question'],
            language=sample['language']
        )

        if result:
            results.append({
                'question': sample['question'],
                'success': True,
                'response_time': result.get('response_time_ms', 0),
                'citations_count': len(result.get('citations', []))
            })
        else:
            results.append({
                'question': sample['question'],
                'success': False
            })

        # Small delay between requests
        import time
        time.sleep(2)

    # Summary
    print("\n\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    successful = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"\nTotal Tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")

    if successful > 0:
        avg_time = sum(r.get('response_time', 0) for r in results if r['success']) / successful
        avg_citations = sum(r.get('citations_count', 0) for r in results if r['success']) / successful
        print(f"Average Response Time: {avg_time:.0f}ms")
        print(f"Average Citations: {avg_citations:.1f}")

    print("\n" + "=" * 80)


def interactive_mode():
    """Interactive mode for testing custom questions"""
    print("=" * 80)
    print("Saudi Law AI Assistant - Interactive Mode")
    print("=" * 80)
    print("\nType your question in Arabic or English (or 'exit' to quit)")
    print("Example: ما هي حقوق الموظف؟")

    if not SUPABASE_ANON_KEY:
        print("\n❌ Error: SUPABASE_ANON_KEY not found in environment variables")
        return

    while True:
        print("\n" + "-" * 80)
        question = input("\nYour question: ").strip()

        if not question:
            continue

        if question.lower() in ['exit', 'quit', 'q']:
            print("\nGoodbye! 👋")
            break

        # Auto-detect language (simple heuristic)
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in question)
        language = 'ar' if has_arabic else 'en'

        test_query(question, language)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # Custom question from command line
        question = ' '.join(sys.argv[1:])
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in question)
        language = 'ar' if has_arabic else 'en'
        test_query(question, language)
    elif '--interactive' in sys.argv or '-i' in sys.argv:
        # Interactive mode
        interactive_mode()
    else:
        # Run all sample tests
        run_all_tests()
        print("\n💡 Tip: Use './test_query.py --interactive' for interactive mode")
        print("💡 Tip: Use './test_query.py \"your question here\"' to test a specific question")
