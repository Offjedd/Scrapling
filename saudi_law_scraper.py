"""
Saudi Arabian Law Scraper
Scrapes laws from https://laws.boe.gov.sa/BoeLaws/Laws/Folders/
and stores them in Supabase database.
"""

import os
import re
import json
from datetime import datetime
from typing import List, Dict, Optional
from scrapling import StealthyFetcher
from supabase import create_client, Client


class SaudiLawScraper:
    """Scraper for Saudi Arabian Law website"""

    def __init__(self):
        """Initialize the scraper with Supabase client"""
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.base_url = "https://laws.boe.gov.sa"
        self.folders_url = f"{self.base_url}/BoeLaws/Laws/Folders/"
        self.fetcher = StealthyFetcher()

    def clean_text(self, text: str) -> str:
        """Clean and normalize Arabic text"""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text

    def extract_date(self, date_str: str) -> Optional[str]:
        """Extract and normalize date from Arabic text"""
        if not date_str:
            return None

        try:
            # Try to extract date patterns (YYYY-MM-DD, DD/MM/YYYY, etc.)
            # This is a placeholder - adjust based on actual date format on the website
            date_str = self.clean_text(date_str)

            # Common patterns in Arabic websites
            patterns = [
                r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
                r'(\d{2})/(\d{2})/(\d{4})',  # DD/MM/YYYY
                r'(\d{4})/(\d{2})/(\d{2})',  # YYYY/MM/DD
            ]

            for pattern in patterns:
                match = re.search(pattern, date_str)
                if match:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # Year first
                        return f"{groups[0]}-{groups[1]}-{groups[2]}"
                    else:  # Day first
                        return f"{groups[2]}-{groups[1]}-{groups[0]}"

            return None
        except Exception as e:
            print(f"Error parsing date '{date_str}': {e}")
            return None

    def scrape_folders(self) -> List[Dict]:
        """Scrape all law folders from the main page"""
        print(f"Fetching folders from: {self.folders_url}")

        try:
            response = self.fetcher.fetch(self.folders_url)

            if not response or response.status != 200:
                print(f"Failed to fetch folders page. Status: {response.status if response else 'None'}")
                return []

            folders = []

            # Find all folder links - adjust selectors based on actual website structure
            # This is a generic approach, may need refinement after inspecting the actual HTML
            folder_elements = response.css('a[href*="/BoeLaws/Laws/Folders/"]').getall()

            if not folder_elements:
                # Try alternative selectors
                folder_elements = response.css('div.folder a, .law-folder a, .folder-item a').getall()

            for element in folder_elements:
                try:
                    # Extract folder information
                    href = element.attrib.get('href', '')

                    if not href or href == self.folders_url:
                        continue

                    # Get folder ID from URL
                    folder_id = href.split('/')[-1] if '/' in href else ''

                    # Make URL absolute
                    if href.startswith('/'):
                        url = f"{self.base_url}{href}"
                    elif not href.startswith('http'):
                        url = f"{self.folders_url}/{href}"
                    else:
                        url = href

                    # Extract folder name
                    name_ar = self.clean_text(element.text)

                    if name_ar and folder_id:
                        folders.append({
                            'folder_id': folder_id,
                            'name_ar': name_ar,
                            'name_en': '',  # Will be filled if available
                            'url': url
                        })
                        print(f"Found folder: {name_ar} (ID: {folder_id})")

                except Exception as e:
                    print(f"Error processing folder element: {e}")
                    continue

            print(f"Total folders found: {len(folders)}")
            return folders

        except Exception as e:
            print(f"Error scraping folders: {e}")
            return []

    def scrape_laws_from_folder(self, folder_url: str, folder_id: str) -> List[Dict]:
        """Scrape all laws from a specific folder"""
        print(f"Fetching laws from folder: {folder_url}")

        try:
            response = self.fetcher.fetch(folder_url)

            if not response or response.status != 200:
                print(f"Failed to fetch folder page. Status: {response.status if response else 'None'}")
                return []

            laws = []

            # Find all law links - adjust selectors based on actual website structure
            law_elements = response.css('a[href*="/BoeLaws/Laws/"]').getall()

            if not law_elements:
                # Try alternative selectors
                law_elements = response.css('div.law a, .law-item a, .law-link a').getall()

            for element in law_elements:
                try:
                    href = element.attrib.get('href', '')

                    if not href or '/Folders/' in href:
                        continue

                    # Make URL absolute
                    if href.startswith('/'):
                        url = f"{self.base_url}{href}"
                    elif not href.startswith('http'):
                        url = f"{self.base_url}{href}"
                    else:
                        url = href

                    # Extract law name
                    name_ar = self.clean_text(element.text)

                    if name_ar:
                        laws.append({
                            'name_ar': name_ar,
                            'url': url,
                            'folder_id': folder_id
                        })
                        print(f"Found law: {name_ar}")

                except Exception as e:
                    print(f"Error processing law element: {e}")
                    continue

            print(f"Total laws found in folder: {len(laws)}")
            return laws

        except Exception as e:
            print(f"Error scraping laws from folder: {e}")
            return []

    def scrape_law_details(self, law_url: str) -> Optional[Dict]:
        """Scrape detailed information from a law page"""
        print(f"Fetching law details from: {law_url}")

        try:
            response = self.fetcher.fetch(law_url)

            if not response or response.status != 200:
                print(f"Failed to fetch law page. Status: {response.status if response else 'None'}")
                return None

            # Extract law details - adjust selectors based on actual website structure
            law_details = {
                'law_number': '',
                'publication_date': None,
                'full_text_ar': '',
                'articles': []
            }

            # Try to extract law number
            law_number_elem = response.css('.law-number, .law-id, [class*="number"]').get()
            if law_number_elem:
                law_details['law_number'] = self.clean_text(law_number_elem.text)

            # Try to extract publication date
            date_elem = response.css('.publication-date, .law-date, [class*="date"]').get()
            if date_elem:
                date_text = self.clean_text(date_elem.text)
                law_details['publication_date'] = self.extract_date(date_text)

            # Extract full text
            content_elem = response.css('.law-content, .law-text, article, main').get()
            if content_elem:
                law_details['full_text_ar'] = self.clean_text(content_elem.text)
            else:
                # Fallback to body text
                law_details['full_text_ar'] = self.clean_text(response.text)

            # Extract articles
            article_elements = response.css('.article, .law-article, [class*="article"]').getall()

            for idx, article_elem in enumerate(article_elements, 1):
                try:
                    # Try to find article number
                    article_num_elem = article_elem.css('.article-number, .article-id, [class*="number"]').get()
                    article_number = self.clean_text(article_num_elem.text) if article_num_elem else str(idx)

                    # Extract article text
                    article_text = self.clean_text(article_elem.text)

                    # Try to extract article title
                    title_elem = article_elem.css('.article-title, h3, h4').get()
                    article_title = self.clean_text(title_elem.text) if title_elem else ''

                    if article_text:
                        law_details['articles'].append({
                            'article_number': article_number,
                            'article_title_ar': article_title,
                            'article_text_ar': article_text
                        })

                except Exception as e:
                    print(f"Error processing article: {e}")
                    continue

            # If no articles found, try to split by common patterns
            if not law_details['articles'] and law_details['full_text_ar']:
                articles = self.split_text_into_articles(law_details['full_text_ar'])
                law_details['articles'] = articles

            return law_details

        except Exception as e:
            print(f"Error scraping law details: {e}")
            return None

    def split_text_into_articles(self, text: str) -> List[Dict]:
        """Split law text into articles using common patterns"""
        articles = []

        # Common Arabic patterns for articles: "المادة الأولى", "المادة 1", "المادة (1)"
        patterns = [
            r'المادة\s+([^\n:]+)[:\n]',
            r'مادة\s+([^\n:]+)[:\n]',
            r'(?:^|\n)(\d+)\s*[.:-]',
        ]

        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.MULTILINE))

            if matches:
                for i, match in enumerate(matches):
                    article_number = self.clean_text(match.group(1))
                    start_pos = match.end()
                    end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                    article_text = self.clean_text(text[start_pos:end_pos])

                    if article_text:
                        articles.append({
                            'article_number': article_number,
                            'article_title_ar': '',
                            'article_text_ar': article_text
                        })

                if articles:
                    break

        return articles

    def save_folder_to_db(self, folder: Dict) -> Optional[str]:
        """Save or update a folder in the database"""
        try:
            # Check if folder exists
            existing = self.supabase.table('law_folders').select('id').eq('folder_id', folder['folder_id']).execute()

            if existing.data:
                # Update existing
                folder_uuid = existing.data[0]['id']
                self.supabase.table('law_folders').update(folder).eq('id', folder_uuid).execute()
                print(f"Updated folder: {folder['name_ar']}")
            else:
                # Insert new
                result = self.supabase.table('law_folders').insert(folder).execute()
                folder_uuid = result.data[0]['id'] if result.data else None
                print(f"Inserted folder: {folder['name_ar']}")

            return folder_uuid

        except Exception as e:
            print(f"Error saving folder to database: {e}")
            return None

    def save_law_to_db(self, law: Dict, folder_uuid: str) -> Optional[str]:
        """Save or update a law in the database"""
        try:
            # Check if law exists
            existing = self.supabase.table('laws').select('id, publication_date').eq('url', law['url']).execute()

            law_data = {
                'name_ar': law['name_ar'],
                'url': law['url'],
                'folder_id': folder_uuid,
                'law_number': law.get('law_number', ''),
                'publication_date': law.get('publication_date'),
                'full_text_ar': law.get('full_text_ar', ''),
                'last_checked_at': datetime.now().isoformat()
            }

            if existing.data:
                law_uuid = existing.data[0]['id']
                old_pub_date = existing.data[0].get('publication_date')
                new_pub_date = law.get('publication_date')

                # Only update if publication date changed or new data available
                if old_pub_date != new_pub_date or law.get('full_text_ar'):
                    self.supabase.table('laws').update(law_data).eq('id', law_uuid).execute()
                    print(f"Updated law: {law['name_ar']}")

                    # If publication date changed, delete old articles and re-insert
                    if old_pub_date != new_pub_date:
                        self.supabase.table('law_articles').delete().eq('law_id', law_uuid).execute()
                        print(f"Deleted old articles for updated law")
                else:
                    print(f"Law unchanged: {law['name_ar']}")
            else:
                # Insert new
                result = self.supabase.table('laws').insert(law_data).execute()
                law_uuid = result.data[0]['id'] if result.data else None
                print(f"Inserted law: {law['name_ar']}")

            return law_uuid

        except Exception as e:
            print(f"Error saving law to database: {e}")
            return None

    def save_articles_to_db(self, articles: List[Dict], law_uuid: str):
        """Save law articles to the database"""
        try:
            for article in articles:
                article_data = {
                    'law_id': law_uuid,
                    'article_number': article['article_number'],
                    'article_title_ar': article.get('article_title_ar', ''),
                    'article_text_ar': article['article_text_ar']
                }

                # Check if article exists
                existing = self.supabase.table('law_articles').select('id').eq('law_id', law_uuid).eq('article_number', article['article_number']).execute()

                if existing.data:
                    # Update existing
                    article_id = existing.data[0]['id']
                    self.supabase.table('law_articles').update(article_data).eq('id', article_id).execute()
                else:
                    # Insert new
                    self.supabase.table('law_articles').insert(article_data).execute()

            print(f"Saved {len(articles)} articles")

        except Exception as e:
            print(f"Error saving articles to database: {e}")

    def run_full_scrape(self):
        """Run complete scraping process"""
        print("=" * 80)
        print("Starting Saudi Arabian Law Scraper")
        print("=" * 80)

        # Step 1: Scrape folders
        folders = self.scrape_folders()

        if not folders:
            print("No folders found. Please check the website structure and selectors.")
            return

        # Step 2: Process each folder
        for folder in folders:
            print(f"\nProcessing folder: {folder['name_ar']}")

            # Save folder to database
            folder_uuid = self.save_folder_to_db(folder)

            if not folder_uuid:
                print(f"Failed to save folder: {folder['name_ar']}")
                continue

            # Scrape laws from this folder
            laws = self.scrape_laws_from_folder(folder['url'], folder['folder_id'])

            # Step 3: Process each law
            for law in laws:
                print(f"\n  Processing law: {law['name_ar']}")

                # Scrape law details
                law_details = self.scrape_law_details(law['url'])

                if law_details:
                    # Merge details
                    law.update(law_details)

                    # Save law to database
                    law_uuid = self.save_law_to_db(law, folder_uuid)

                    if law_uuid and law.get('articles'):
                        # Save articles
                        self.save_articles_to_db(law['articles'], law_uuid)

        print("\n" + "=" * 80)
        print("Scraping completed!")
        print("=" * 80)

    def run_update_check(self):
        """Check for updates to existing laws (daily update)"""
        print("=" * 80)
        print("Checking for law updates")
        print("=" * 80)

        try:
            # Get all laws from database
            laws = self.supabase.table('laws').select('id, url, publication_date, name_ar').execute()

            if not laws.data:
                print("No laws in database. Run full scrape first.")
                return

            print(f"Checking {len(laws.data)} laws for updates...")

            for law_record in laws.data:
                print(f"\nChecking: {law_record['name_ar']}")

                # Scrape current law details
                law_details = self.scrape_law_details(law_record['url'])

                if not law_details:
                    continue

                # Check if publication date changed
                old_date = law_record.get('publication_date')
                new_date = law_details.get('publication_date')

                if old_date != new_date:
                    print(f"  Publication date changed: {old_date} -> {new_date}")

                    # Update law
                    update_data = {
                        'publication_date': new_date,
                        'law_number': law_details.get('law_number', ''),
                        'full_text_ar': law_details.get('full_text_ar', ''),
                        'last_checked_at': datetime.now().isoformat()
                    }

                    self.supabase.table('laws').update(update_data).eq('id', law_record['id']).execute()

                    # Delete old articles and insert new ones
                    self.supabase.table('law_articles').delete().eq('law_id', law_record['id']).execute()

                    if law_details.get('articles'):
                        self.save_articles_to_db(law_details['articles'], law_record['id'])

                    print(f"  Law updated successfully")
                else:
                    # Just update last_checked_at
                    self.supabase.table('laws').update({'last_checked_at': datetime.now().isoformat()}).eq('id', law_record['id']).execute()
                    print(f"  No changes detected")

            print("\n" + "=" * 80)
            print("Update check completed!")
            print("=" * 80)

        except Exception as e:
            print(f"Error during update check: {e}")


def main():
    """Main entry point"""
    import sys

    scraper = SaudiLawScraper()

    if len(sys.argv) > 1 and sys.argv[1] == 'update':
        # Run update check
        scraper.run_update_check()
    else:
        # Run full scrape
        scraper.run_full_scrape()


if __name__ == '__main__':
    main()
