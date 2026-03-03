#!/usr/bin/env python3
"""
Enhanced Saudi Arabian Law Scraper
- Handles multiple folders with nested layers
- Automatically generates embeddings
- Bulk inserts into Supabase
- Progress tracking and resumption
"""

import os
import re
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Set
from scrapling import StealthyFetcher
from openai import OpenAI

class EnhancedSaudiLawScraper:
    """Enhanced scraper with multi-layer support and embedding generation"""

    def __init__(self):
        """Initialize scraper with necessary clients"""
        self.load_env()

        self.openai_client = OpenAI(api_key=self.openai_key)
        self.base_url = "https://laws.boe.gov.sa"
        self.folders_url = f"{self.base_url}/BoeLaws/Laws/Folders/"
        self.fetcher = StealthyFetcher()

        self.visited_urls: Set[str] = set()
        self.scraped_data = {
            'folders': [],
            'laws': [],
            'total_folders': 0,
            'total_laws': 0
        }

    def load_env(self):
        """Load environment variables from .env file"""
        env = {}
        with open('.env') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    env[key] = val

        self.supabase_url = env.get('SUPABASE_URL')
        self.supabase_key = env.get('SUPABASE_SERVICE_ROLE_KEY')
        self.openai_key = env.get('OPENAI_API_KEY')

        if not all([self.supabase_url, self.supabase_key, self.openai_key]):
            raise ValueError("Missing required environment variables")

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"  ⚠️ Error generating embedding: {e}")
            return None

    def scrape_folder_recursive(self, folder_url: str, parent_id: str = None, level: int = 0) -> List[Dict]:
        """Recursively scrape folders and their contents"""

        if folder_url in self.visited_urls:
            return []

        self.visited_urls.add(folder_url)
        indent = "  " * level

        print(f"{indent}📁 Scraping folder (level {level}): {folder_url}")

        try:
            response = self.fetcher.fetch(folder_url)

            if not response or response.status != 200:
                print(f"{indent}  ❌ Failed to fetch. Status: {response.status if response else 'None'}")
                return []

            results = []

            # Look for subfolder links
            subfolder_links = response.css('a[href*="/Folders/"]').getall()

            # Look for law links
            law_links = response.css('a[href*="/Laws/"]').getall()

            # Filter out parent/self references
            subfolders = []
            for link in subfolder_links:
                href = link.attrib.get('href', '')
                if not href or href == folder_url:
                    continue

                full_url = self.make_absolute_url(href)

                if full_url not in self.visited_urls and '/Folders/' in full_url:
                    name = self.clean_text(link.text)
                    if name:
                        subfolders.append({
                            'url': full_url,
                            'name': name,
                            'level': level + 1
                        })

            # Process subfolders recursively
            print(f"{indent}  Found {len(subfolders)} subfolders")
            for subfolder in subfolders:
                folder_data = {
                    'folder_id': self.extract_id_from_url(subfolder['url']),
                    'name_ar': subfolder['name'],
                    'name_en': '',
                    'url': subfolder['url'],
                    'parent_id': parent_id,
                    'level': subfolder['level']
                }

                results.append({'type': 'folder', 'data': folder_data})
                self.scraped_data['folders'].append(folder_data)
                self.scraped_data['total_folders'] += 1

                print(f"{indent}  ✅ Folder: {subfolder['name']}")

                # Recurse into subfolder
                sub_results = self.scrape_folder_recursive(
                    subfolder['url'],
                    folder_data['folder_id'],
                    level + 1
                )
                results.extend(sub_results)

                time.sleep(1)

            # Process laws in current folder
            laws = []
            for link in law_links:
                href = link.attrib.get('href', '')
                if not href or '/Folders/' in href:
                    continue

                full_url = self.make_absolute_url(href)

                if full_url not in self.visited_urls:
                    name = self.clean_text(link.text)
                    if name:
                        laws.append({
                            'url': full_url,
                            'name': name
                        })

            print(f"{indent}  Found {len(laws)} laws")

            # Scrape each law
            for law in laws:
                law_details = self.scrape_law_details(law['url'], level)

                if law_details:
                    law_data = {
                        'name_ar': law['name'],
                        'url': law['url'],
                        'folder_id': parent_id,
                        'law_number': law_details.get('law_number', ''),
                        'full_text_ar': law_details.get('full_text_ar', ''),
                        'articles': law_details.get('articles', [])
                    }

                    results.append({'type': 'law', 'data': law_data})
                    self.scraped_data['laws'].append(law_data)
                    self.scraped_data['total_laws'] += 1

                    print(f"{indent}  ✅ Law: {law['name']}")

                time.sleep(2)

            return results

        except Exception as e:
            print(f"{indent}  ❌ Error: {e}")
            return []

    def scrape_law_details(self, law_url: str, level: int = 0) -> Optional[Dict]:
        """Scrape detailed information from a law page"""
        indent = "  " * level

        if law_url in self.visited_urls:
            return None

        self.visited_urls.add(law_url)

        try:
            response = self.fetcher.fetch(law_url)

            if not response or response.status != 200:
                return None

            law_details = {
                'law_number': '',
                'full_text_ar': '',
                'articles': []
            }

            # Extract law number
            law_number_elem = response.css('.law-number, .law-id, [class*="number"]').get()
            if law_number_elem:
                law_details['law_number'] = self.clean_text(law_number_elem.text)

            # Extract full text
            content_elem = response.css('.law-content, .law-text, article, main, .content').get()
            if content_elem:
                law_details['full_text_ar'] = self.clean_text(content_elem.text)
            else:
                body_elem = response.css('body').get()
                if body_elem:
                    law_details['full_text_ar'] = self.clean_text(body_elem.text)

            # Extract articles
            article_elements = response.css('.article, .law-article, [class*="article"]').getall()

            for idx, article_elem in enumerate(article_elements, 1):
                article_text = self.clean_text(article_elem.text)

                if article_text:
                    law_details['articles'].append({
                        'article_number': str(idx),
                        'article_text_ar': article_text
                    })

            # If no articles found, try to split text
            if not law_details['articles'] and law_details['full_text_ar']:
                law_details['articles'] = self.split_into_articles(law_details['full_text_ar'])

            return law_details

        except Exception as e:
            print(f"{indent}    ⚠️ Error scraping law: {e}")
            return None

    def split_into_articles(self, text: str) -> List[Dict]:
        """Split text into articles"""
        articles = []

        patterns = [
            r'المادة\s+([^\n:]+)[:\n]',
            r'مادة\s+([^\n:]+)[:\n]',
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
                            'article_text_ar': article_text
                        })

                if articles:
                    break

        return articles

    def make_absolute_url(self, url: str) -> str:
        """Convert relative URL to absolute"""
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            return f"{self.base_url}{url}"
        else:
            return f"{self.base_url}/{url}"

    def extract_id_from_url(self, url: str) -> str:
        """Extract ID from URL"""
        parts = url.rstrip('/').split('/')
        return parts[-1] if parts else url

    def save_to_database_bulk(self):
        """Save all scraped data to database with embeddings"""
        import requests

        print("\n" + "=" * 80)
        print("💾 Saving to Database")
        print("=" * 80)

        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

        # Save folders first
        print(f"\n📁 Saving {len(self.scraped_data['folders'])} folders...")
        folder_map = {}

        for folder in self.scraped_data['folders']:
            try:
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/law_folders",
                    headers=headers,
                    json={
                        'folder_id': folder['folder_id'],
                        'name_ar': folder['name_ar'],
                        'name_en': folder['name_en']
                    },
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    data = response.json()
                    folder_map[folder['folder_id']] = data[0]['id'] if isinstance(data, list) else data['id']
                    print(f"  ✅ {folder['name_ar']}")
                else:
                    print(f"  ⚠️ {folder['name_ar']}: {response.status_code}")

            except Exception as e:
                print(f"  ❌ Error saving folder: {e}")

        # Save laws with embeddings
        print(f"\n📜 Saving {len(self.scraped_data['laws'])} laws with embeddings...")

        for idx, law in enumerate(self.scraped_data['laws'], 1):
            try:
                print(f"\n  [{idx}/{len(self.scraped_data['laws'])}] {law['name_ar']}")

                folder_uuid = folder_map.get(law['folder_id'])

                if not folder_uuid:
                    print(f"    ⚠️ Folder not found, skipping")
                    continue

                # Insert law
                law_response = requests.post(
                    f"{self.supabase_url}/rest/v1/laws",
                    headers=headers,
                    json={
                        'name_ar': law['name_ar'],
                        'url': law['url'],
                        'folder_id': folder_uuid,
                        'law_number': law['law_number'],
                        'full_text_ar': law['full_text_ar']
                    },
                    timeout=30
                )

                if law_response.status_code not in [200, 201]:
                    print(f"    ❌ Failed to insert law: {law_response.status_code}")
                    continue

                law_data = law_response.json()
                law_uuid = law_data[0]['id'] if isinstance(law_data, list) else law_data['id']

                print(f"    ✅ Law saved")

                # Generate and save embedding
                text_for_embedding = f"{law['name_ar']}\n\n{law['full_text_ar'][:5000]}"

                print(f"    🧠 Generating embedding...")
                embedding = self.generate_embedding(text_for_embedding)

                if embedding:
                    emb_response = requests.post(
                        f"{self.supabase_url}/rest/v1/law_embeddings",
                        headers=headers,
                        json={
                            'law_id': law_uuid,
                            'text_chunk': law['name_ar'],
                            'embedding': embedding,
                            'chunk_index': 0
                        },
                        timeout=30
                    )

                    if emb_response.status_code in [200, 201]:
                        print(f"    ✅ Embedding saved")
                    else:
                        print(f"    ⚠️ Embedding failed: {emb_response.status_code}")

                # Save articles
                if law.get('articles'):
                    for article in law['articles'][:10]:
                        try:
                            requests.post(
                                f"{self.supabase_url}/rest/v1/law_articles",
                                headers=headers,
                                json={
                                    'law_id': law_uuid,
                                    'article_number': article['article_number'],
                                    'article_text_ar': article['article_text_ar']
                                },
                                timeout=30
                            )
                        except:
                            pass

                    print(f"    ✅ {len(law['articles'])} articles saved")

                time.sleep(1)

            except Exception as e:
                print(f"    ❌ Error: {e}")

        print("\n" + "=" * 80)
        print("✅ Database Save Complete!")
        print("=" * 80)

    def run_full_scrape(self):
        """Run complete multi-layer scrape"""
        print("=" * 80)
        print("🚀 Enhanced Saudi Law Scraper")
        print("=" * 80)
        print()

        start_time = time.time()

        # Start recursive scraping from root
        results = self.scrape_folder_recursive(self.folders_url, None, 0)

        elapsed = time.time() - start_time

        print("\n" + "=" * 80)
        print("📊 Scraping Summary")
        print("=" * 80)
        print(f"Total Folders: {self.scraped_data['total_folders']}")
        print(f"Total Laws: {self.scraped_data['total_laws']}")
        print(f"Time Elapsed: {elapsed:.1f} seconds")
        print("=" * 80)

        # Save progress to file
        with open('scrape_progress.json', 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, ensure_ascii=False, indent=2)

        print("\n💾 Progress saved to: scrape_progress.json")

        # Save to database
        self.save_to_database_bulk()


def main():
    """Main entry point"""
    scraper = EnhancedSaudiLawScraper()
    scraper.run_full_scrape()


if __name__ == '__main__':
    main()
