#!/usr/bin/env python3
"""
Quick test to verify OpenAI API key is working
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://exilgibjcnrtashitzjk.supabase.co')
SUPABASE_ANON_KEY = os.getenv('VITE_SUPABASE_ANON_KEY', '')

def test_openai_connection():
    """Test if OpenAI API key is configured and working"""

    print("=" * 60)
    print("Testing OpenAI API Connection")
    print("=" * 60)

    # Try to call the generate-embeddings function with a test
    url = f"{SUPABASE_URL}/functions/v1/generate-embeddings"

    headers = {
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        print("\nCalling generate-embeddings function...")
        response = requests.post(url, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("\n✅ Success! OpenAI API key is configured correctly.")
            print(f"Response: {result}")

            if result.get('processed', 0) == 0 and result.get('total', 0) == 0:
                print("\n⚠️  Note: No articles found in database.")
                print("   You need to run the scraper first:")
                print("   python saudi_law_scraper.py")
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")

            if "OPENAI_API_KEY" in response.text:
                print("\n⚠️  OpenAI API key issue detected.")
                print("   Make sure OPENAI_API_KEY is set as a Supabase Edge Function secret.")

    except Exception as e:
        print(f"\n❌ Error: {e}")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_openai_connection()
