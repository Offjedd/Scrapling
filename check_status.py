#!/usr/bin/env python3
"""
Check the status of the Saudi Law AI system
Shows what's been completed and what still needs to be done
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_status():
    """Check the status of all system components"""

    print("=" * 80)
    print("Saudi Law AI Assistant - System Status Check")
    print("=" * 80)
    print()

    # Check environment variables
    print("1. Environment Configuration:")
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')

    if supabase_url:
        print(f"   ✅ SUPABASE_URL configured")
    else:
        print(f"   ❌ SUPABASE_URL missing")

    if supabase_key:
        print(f"   ✅ SUPABASE_SERVICE_ROLE_KEY configured")
    else:
        print(f"   ❌ SUPABASE_SERVICE_ROLE_KEY missing")

    if openai_key:
        print(f"   ✅ OPENAI_API_KEY configured")
    else:
        print(f"   ⚠️  OPENAI_API_KEY missing (check Supabase secrets)")

    print()

    # Check database
    if not supabase_url or not supabase_key:
        print("Cannot check database - credentials missing")
        return

    try:
        print("2. Database Status:")
        supabase = create_client(supabase_url, supabase_key)

        # Count folders
        folders = supabase.table('law_folders').select('id', count='exact').execute()
        folder_count = folders.count if folders.count else 0
        print(f"   {'✅' if folder_count > 0 else '❌'} Law Folders: {folder_count}")

        # Count laws
        laws = supabase.table('laws').select('id', count='exact').execute()
        law_count = laws.count if laws.count else 0
        print(f"   {'✅' if law_count > 0 else '❌'} Laws: {law_count}")

        # Count articles
        articles = supabase.table('law_articles').select('id', count='exact').execute()
        article_count = articles.count if articles.count else 0
        print(f"   {'✅' if article_count > 0 else '❌'} Articles: {article_count}")

        # Count embeddings
        embeddings = supabase.table('law_embeddings').select('id', count='exact').execute()
        embedding_count = embeddings.count if embeddings.count else 0
        embedding_percentage = (embedding_count / article_count * 100) if article_count > 0 else 0
        print(f"   {'✅' if embedding_count > 0 else '❌'} Embeddings: {embedding_count} ({embedding_percentage:.1f}% of articles)")

        # Count queries
        queries = supabase.table('query_logs').select('id', count='exact').execute()
        query_count = queries.count if queries.count else 0
        print(f"   ℹ️  Query Logs: {query_count}")

        print()

        # System readiness
        print("3. System Readiness:")

        if folder_count == 0:
            print("   ⚠️  Status: NOT READY")
            print("   ❌ No laws in database")
            print()
            print("   Next Step: Run the scraper")
            print("   Command: python3 saudi_law_scraper.py")

        elif embedding_count == 0:
            print("   ⚠️  Status: PARTIALLY READY")
            print("   ✅ Laws scraped successfully")
            print("   ❌ Embeddings not generated")
            print()
            print("   Next Step: Generate embeddings")
            print("   Command: curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/generate-embeddings \\")
            print("              -H \"Authorization: Bearer YOUR_ANON_KEY\"")

        elif embedding_count < article_count:
            print("   ⚠️  Status: ALMOST READY")
            print("   ✅ Laws scraped successfully")
            print(f"   ⚠️  Embeddings: {embedding_percentage:.1f}% complete")
            print()
            print("   Next Step: Generate remaining embeddings")
            print("   Command: Run the embeddings API again (processes 100 at a time)")

        else:
            print("   ✅ Status: FULLY READY!")
            print("   ✅ Laws scraped")
            print("   ✅ Embeddings generated")
            print()
            print("   You can now use the system:")
            print("   - Open web/index.html in your browser")
            print("   - Or run: python3 test_query.py --interactive")

    except Exception as e:
        print(f"   ❌ Error checking database: {e}")

    print()
    print("=" * 80)


if __name__ == '__main__':
    check_status()
