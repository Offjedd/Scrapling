"""
Database Validation Script
Checks completeness and quality of scraped law data
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

load_dotenv()


class DatabaseValidator:
    """Validates the completeness of law database"""

    def __init__(self):
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

        self.supabase: Client = create_client(supabase_url, supabase_key)

    def print_section(self, title: str):
        """Print a section header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)

    def get_basic_counts(self):
        """Get basic counts from all tables"""
        self.print_section("BASIC STATISTICS")

        folders_count = self.supabase.table('law_folders').select('id', count='exact').execute()
        laws_count = self.supabase.table('laws').select('id', count='exact').execute()
        articles_count = self.supabase.table('law_articles').select('id', count='exact').execute()
        embeddings_count = self.supabase.table('law_embeddings').select('id', count='exact').execute()

        print(f"\nTotal Records:")
        print(f"  Folders:    {folders_count.count:>6}")
        print(f"  Laws:       {laws_count.count:>6}")
        print(f"  Articles:   {articles_count.count:>6}")
        print(f"  Embeddings: {embeddings_count.count:>6}")

        return {
            'folders': folders_count.count,
            'laws': laws_count.count,
            'articles': articles_count.count,
            'embeddings': embeddings_count.count
        }

    def check_laws_without_articles(self):
        """Find laws that have no articles"""
        self.print_section("LAWS WITHOUT ARTICLES")

        # Get all laws
        all_laws = self.supabase.table('laws').select('id, name_ar, url').execute()

        # Get laws with articles
        laws_with_articles = self.supabase.table('law_articles').select('law_id').execute()
        law_ids_with_articles = set(article['law_id'] for article in laws_with_articles.data)

        # Find laws without articles
        laws_without_articles = [
            law for law in all_laws.data
            if law['id'] not in law_ids_with_articles
        ]

        print(f"\nLaws without articles: {len(laws_without_articles)}")

        if laws_without_articles:
            print("\nFirst 10 laws without articles:")
            for i, law in enumerate(laws_without_articles[:10], 1):
                print(f"  {i}. {law['name_ar'][:60]}")
                print(f"     URL: {law['url']}")

        return laws_without_articles

    def check_articles_without_embeddings(self):
        """Find articles that have no embeddings"""
        self.print_section("ARTICLES WITHOUT EMBEDDINGS")

        # Get all articles
        all_articles = self.supabase.table('law_articles').select('id, article_number, law_id').execute()

        # Get articles with embeddings
        articles_with_embeddings = self.supabase.table('law_embeddings').select('article_id').execute()
        article_ids_with_embeddings = set(
            emb['article_id'] for emb in articles_with_embeddings.data
            if emb['article_id'] is not None
        )

        # Find articles without embeddings
        articles_without_embeddings = [
            article for article in all_articles.data
            if article['id'] not in article_ids_with_embeddings
        ]

        print(f"\nArticles without embeddings: {len(articles_without_embeddings)}")

        if articles_without_embeddings:
            print(f"\nFirst 10 articles without embeddings:")
            for i, article in enumerate(articles_without_embeddings[:10], 1):
                print(f"  {i}. Article {article['article_number']} (Law ID: {article['law_id'][:8]}...)")

        return articles_without_embeddings

    def get_articles_per_law_stats(self):
        """Calculate statistics on articles per law"""
        self.print_section("ARTICLES PER LAW STATISTICS")

        # Get article counts per law
        result = self.supabase.rpc('get_articles_per_law_stats').execute()

        # If RPC doesn't exist, calculate manually
        laws = self.supabase.table('laws').select('id, name_ar').execute()
        articles = self.supabase.table('law_articles').select('law_id').execute()

        # Count articles per law
        article_counts = {}
        for article in articles.data:
            law_id = article['law_id']
            article_counts[law_id] = article_counts.get(law_id, 0) + 1

        # Calculate statistics
        counts = list(article_counts.values())
        if counts:
            avg = sum(counts) / len(counts)
            max_count = max(counts)
            min_count = min(counts)
            median = sorted(counts)[len(counts) // 2]

            print(f"\nArticle count statistics:")
            print(f"  Average:  {avg:.1f}")
            print(f"  Median:   {median}")
            print(f"  Maximum:  {max_count}")
            print(f"  Minimum:  {min_count}")

            # Find law with most articles
            max_law_id = [k for k, v in article_counts.items() if v == max_count][0]
            max_law = [law for law in laws.data if law['id'] == max_law_id][0]

            print(f"\nLaw with most articles ({max_count} articles):")
            print(f"  {max_law['name_ar'][:70]}")

            # Find law with least articles
            min_law_id = [k for k, v in article_counts.items() if v == min_count][0]
            min_law = [law for law in laws.data if law['id'] == min_law_id][0]

            print(f"\nLaw with fewest articles ({min_count} articles):")
            print(f"  {min_law['name_ar'][:70]}")

        return article_counts

    def check_folder_distribution(self):
        """Show distribution of laws across folders"""
        self.print_section("FOLDER DISTRIBUTION")

        folders = self.supabase.table('law_folders').select('id, name_ar').execute()
        laws = self.supabase.table('laws').select('folder_id').execute()

        # Count laws per folder
        folder_counts = {}
        for law in laws.data:
            folder_id = law['folder_id']
            if folder_id:
                folder_counts[folder_id] = folder_counts.get(folder_id, 0) + 1

        print(f"\nLaws per folder:")
        for folder in folders.data:
            count = folder_counts.get(folder['id'], 0)
            print(f"  {folder['name_ar'][:50]:<50} {count:>5} laws")

        # Count laws without folder
        laws_without_folder = sum(1 for law in laws.data if not law['folder_id'])
        if laws_without_folder > 0:
            print(f"\n  Laws without folder: {laws_without_folder}")

    def check_data_quality(self):
        """Check various data quality metrics"""
        self.print_section("DATA QUALITY CHECKS")

        # Check for empty law names
        empty_names = self.supabase.table('laws').select('id').or_('name_ar.is.null,name_ar.eq.').execute()
        print(f"\nLaws with empty names: {len(empty_names.data)}")

        # Check for empty article text
        empty_articles = self.supabase.table('law_articles').select('id').or_('article_text_ar.is.null,article_text_ar.eq.').execute()
        print(f"Articles with empty text: {len(empty_articles.data)}")

        # Check for duplicate URLs
        laws = self.supabase.table('laws').select('url').execute()
        urls = [law['url'] for law in laws.data]
        duplicates = len(urls) - len(set(urls))
        print(f"Duplicate law URLs: {duplicates}")

        # Check for very short articles (potential extraction errors)
        short_articles = self.supabase.table('law_articles').select('id, article_text_ar').execute()
        very_short = [a for a in short_articles.data if len(a.get('article_text_ar', '')) < 20]
        print(f"Very short articles (<20 chars): {len(very_short)}")

        # Check for laws without publication date
        no_date = self.supabase.table('laws').select('id, name_ar').is_('publication_date', 'null').execute()
        print(f"Laws without publication date: {len(no_date.data)}")

        if no_date.data:
            print("\nFirst 5 laws without dates:")
            for i, law in enumerate(no_date.data[:5], 1):
                print(f"  {i}. {law['name_ar'][:60]}")

    def check_recent_updates(self):
        """Show recently updated laws"""
        self.print_section("RECENT UPDATES")

        recent = self.supabase.table('laws').select('name_ar, last_checked_at').order('last_checked_at', desc=True).limit(5).execute()

        if recent.data:
            print("\nMost recently checked laws:")
            for i, law in enumerate(recent.data, 1):
                checked = law.get('last_checked_at', 'Never')
                print(f"  {i}. {law['name_ar'][:60]}")
                print(f"     Last checked: {checked}")

    def generate_summary_report(self):
        """Generate a complete summary report"""
        self.print_section("DATABASE VALIDATION REPORT")

        print(f"\nReport generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Get all data
        counts = self.get_basic_counts()
        laws_no_articles = self.check_laws_without_articles()
        articles_no_embeddings = self.check_articles_without_embeddings()
        self.get_articles_per_law_stats()
        self.check_folder_distribution()
        self.check_data_quality()
        self.check_recent_updates()

        # Overall health score
        self.print_section("DATABASE HEALTH SCORE")

        total_score = 100
        issues = []

        if counts['laws'] == 0:
            issues.append("No laws in database")
            total_score -= 50

        if counts['laws'] > 0 and counts['articles'] == 0:
            issues.append("No articles extracted")
            total_score -= 30

        if len(laws_no_articles) > counts['laws'] * 0.1:
            issues.append(f"More than 10% of laws have no articles ({len(laws_no_articles)})")
            total_score -= 20

        if len(articles_no_embeddings) > counts['articles'] * 0.1:
            issues.append(f"More than 10% of articles have no embeddings ({len(articles_no_embeddings)})")
            total_score -= 20

        if counts['folders'] == 0:
            issues.append("No folders in database")
            total_score -= 10

        print(f"\nHealth Score: {max(0, total_score)}/100")

        if issues:
            print("\nIssues detected:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\nNo major issues detected!")

        # Recommendations
        print("\nRecommendations:")
        if counts['laws'] == 0:
            print("  1. Run the enhanced_law_scraper.py to populate the database")
        elif len(laws_no_articles) > 0:
            print(f"  1. Re-scrape {len(laws_no_articles)} laws without articles")
        elif len(articles_no_embeddings) > 0:
            print(f"  1. Generate embeddings for {len(articles_no_embeddings)} articles")
        else:
            print("  1. Database is complete! Set up regular update checks")
            print("  2. Test the search functionality with sample queries")
            print("  3. Build the frontend application")

        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    validator = DatabaseValidator()
    validator.generate_summary_report()


if __name__ == '__main__':
    main()
