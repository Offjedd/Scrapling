"""
Enhanced Saudi Arabian Law Scraper with Article-Level Extraction
Scrapes complete law data including individual articles and generates embeddings
"""

import os
import re
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from scrapling import StealthyFetcher
from supabase import create_client, Client
import openai

# Load environment variables
load_dotenv()


class EnhancedLawScraper:
    """Enhanced scraper with article-level extraction and embeddings"""

    def __init__(self):
        """Initialize the scraper with Supabase and OpenAI clients"""
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
        openai_key = os.environ.get('OPENAI_API_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.base_url = "https://laws.boe.gov.sa"
        self.folders_url = f"{self.base_url}/BoeLaws/Laws/Folders/"
        self.fetcher = StealthyFetcher()

        # Initialize OpenAI for embeddings
        if openai_key:
            openai.api_key = openai_key
            self.has_openai = True
        else:
            print("Warning: OPENAI_API_KEY not set. Embeddings will be skipped.")
            self.has_openai = False

        # Statistics
        self.stats = {
            'folders_processed': 0,
            'laws_processed': 0,
            'articles_extracted': 0,
            'embeddings_generated': 0,
            'errors': []
        }

    def clean_text(self, text: str) -> str:
        """Clean and normalize Arabic text"""
        if not text:
            return ""

        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Remove common unwanted characters
        text = text.replace('\u200f', '')  # Right-to-left mark
        text = text.replace('\u200e', '')  # Left-to-right mark

        return text

    def extract_law_metadata(self, response) -> Dict:
        """Extract metadata from law page header"""
        metadata = {
            'law_number': '',
            'publication_date': None,
            'status': '',
            'category': ''
        }

        try:
            # Try multiple selectors for law number
            for selector in ['.law-number', '.law-id', '[class*="number"]', 'div:contains("عدد مرات")']:
                elem = response.css(selector).get()
                if elem:
                    text = self.clean_text(elem.text)
                    # Extract number from text
                    match = re.search(r'\d+', text)
                    if match:
                        metadata['law_number'] = match.group(0)
                        break

            # Try to extract publication date
            for selector in ['.publication-date', '.law-date', '[class*="date"]', 'div:contains("التاريخ")']:
                elem = response.css(selector).get()
                if elem:
                    date_text = self.clean_text(elem.text)
                    # Extract date patterns
                    date = self.extract_date(date_text)
                    if date:
                        metadata['publication_date'] = date
                        break

        except Exception as e:
            print(f"Error extracting metadata: {e}")

        return metadata

    def extract_date(self, date_str: str) -> Optional[str]:
        """Extract and normalize date from text"""
        if not date_str:
            return None

        try:
            date_str = self.clean_text(date_str)

            # Common date patterns
            patterns = [
                r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
                r'(\d{2})/(\d{2})/(\d{4})',  # DD/MM/YYYY
                r'(\d{4})/(\d{2})/(\d{2})',  # YYYY/MM/DD
                r'(\d{2})\s*/\s*(\d{2})\s*/\s*(\d{4})',  # DD / MM / YYYY with spaces
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

    def extract_articles_from_html(self, response) -> List[Dict]:
        """Extract individual articles from the law text section"""
        articles = []

        try:
            # Look for the law text container - try multiple strategies
            law_text_container = None

            # Strategy 1: Find container with "نص النظام" heading
            law_text_heading = response.css('*:contains("نص النظام")').get()
            if law_text_heading:
                # Get the parent container
                container = law_text_heading.parent
                while container and container.name != 'body':
                    # Look for a container that has multiple article divs
                    article_divs = container.css('div:contains("المادة"), div:contains("مادة")').getall()
                    if len(article_divs) >= 2:
                        law_text_container = container
                        break
                    container = container.parent

            # Strategy 2: Find all elements containing article markers
            if not law_text_container:
                law_text_container = response

            # Extract articles using multiple patterns
            article_elements = law_text_container.css('div:contains("المادة"), p:contains("المادة"), div:contains("مادة")').getall()

            # Process each potential article element
            for elem in article_elements:
                text = self.clean_text(elem.text)

                # Skip if too short or doesn't look like an article
                if len(text) < 10:
                    continue

                # Try to extract article number and title
                article_data = self.parse_article_text(text)
                if article_data:
                    articles.append(article_data)

            # If no articles found with HTML parsing, try text-based extraction
            if not articles:
                full_text = self.clean_text(law_text_container.text)
                articles = self.split_text_into_articles(full_text)

        except Exception as e:
            print(f"Error extracting articles from HTML: {e}")

        return articles

    def parse_article_text(self, text: str) -> Optional[Dict]:
        """Parse individual article text to extract number, title, and content"""
        try:
            # Pattern: المادة الأولى / المادة (1) / المادة 1
            patterns = [
                r'المادة\s+(الأولى|الثانية|الثالثة|الرابعة|الخامسة|السادسة|السابعة|الثامنة|التاسعة|العاشرة)',
                r'المادة\s*\((\d+)\)',
                r'المادة\s+(\d+)',
                r'مادة\s*\((\d+)\)',
                r'مادة\s+(\d+)',
            ]

            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    article_number = match.group(1)

                    # Convert Arabic number words to digits
                    arabic_numbers = {
                        'الأولى': '1', 'الثانية': '2', 'الثالثة': '3',
                        'الرابعة': '4', 'الخامسة': '5', 'السادسة': '6',
                        'السابعة': '7', 'الثامنة': '8', 'التاسعة': '9',
                        'العاشرة': '10'
                    }

                    if article_number in arabic_numbers:
                        article_number = arabic_numbers[article_number]

                    # Extract content (everything after the article marker)
                    content_start = match.end()
                    article_content = text[content_start:].strip()

                    # Try to extract title if present (usually after a colon or in next line)
                    title = ''
                    title_match = re.match(r'^[:\s]*([^\n.]+)[:\n.]', article_content)
                    if title_match:
                        potential_title = title_match.group(1).strip()
                        # If the title is short and looks like a heading, extract it
                        if len(potential_title) < 100 and not re.search(r'[.،]', potential_title):
                            title = potential_title
                            article_content = article_content[len(potential_title):].strip()

                    return {
                        'article_number': article_number,
                        'article_title_ar': title,
                        'article_text_ar': article_content
                    }

            return None

        except Exception as e:
            print(f"Error parsing article text: {e}")
            return None

    def split_text_into_articles(self, text: str) -> List[Dict]:
        """Split law text into articles using pattern matching"""
        articles = []

        try:
            # Comprehensive patterns for article detection
            patterns = [
                r'المادة\s+(الأولى|الثانية|الثالثة|الرابعة|الخامسة|السادسة|السابعة|الثامنة|التاسعة|العاشرة|[\u0660-\u0669\d]+)',
                r'المادة\s*[\(（]([^)）]+)[\)）]',
                r'مادة\s+([\u0660-\u0669\d]+)',
            ]

            # Convert Arabic-Indic digits to Western digits
            text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))

            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))

                if len(matches) >= 2:  # Need at least 2 articles
                    for i, match in enumerate(matches):
                        article_number = match.group(1).strip()

                        # Convert Arabic number words
                        arabic_numbers = {
                            'الأولى': '1', 'الثانية': '2', 'الثالثة': '3',
                            'الرابعة': '4', 'الخامسة': '5', 'السادسة': '6',
                            'السابعة': '7', 'الثامنة': '8', 'التاسعة': '9',
                            'العاشرة': '10'
                        }

                        if article_number in arabic_numbers:
                            article_number = arabic_numbers[article_number]

                        start_pos = match.end()
                        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                        article_text = self.clean_text(text[start_pos:end_pos])

                        if article_text and len(article_text) > 10:
                            articles.append({
                                'article_number': article_number,
                                'article_title_ar': '',
                                'article_text_ar': article_text
                            })

                    if articles:
                        break  # Found articles, stop trying patterns

        except Exception as e:
            print(f"Error splitting text into articles: {e}")

        return articles

    def scrape_law_details(self, law_url: str) -> Optional[Dict]:
        """Scrape complete law details including all articles"""
        print(f"  Fetching: {law_url}")

        try:
            response = self.fetcher.fetch(law_url)

            if not response or response.status != 200:
                print(f"  Failed to fetch. Status: {response.status if response else 'None'}")
                self.stats['errors'].append({'url': law_url, 'error': 'Failed to fetch'})
                return None

            # Extract metadata
            metadata = self.extract_law_metadata(response)

            # Extract full text
            full_text = ''
            for selector in ['.law-content', '.law-text', 'article', 'main', 'div[class*="content"]']:
                elem = response.css(selector).get()
                if elem:
                    full_text = self.clean_text(elem.text)
                    if len(full_text) > 100:
                        break

            # Fallback to body if no content found
            if len(full_text) < 100:
                full_text = self.clean_text(response.text)

            # Extract articles
            articles = self.extract_articles_from_html(response)

            law_details = {
                'law_number': metadata['law_number'],
                'publication_date': metadata['publication_date'],
                'full_text_ar': full_text,
                'articles': articles,
                'metadata': metadata
            }

            print(f"  Extracted {len(articles)} articles")
            self.stats['articles_extracted'] += len(articles)

            return law_details

        except Exception as e:
            print(f"  Error scraping law: {e}")
            self.stats['errors'].append({'url': law_url, 'error': str(e)})
            return None

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text using OpenAI"""
        if not self.has_openai or not text:
            return None

        try:
            # Truncate text if too long (max 8191 tokens for text-embedding-3-small)
            max_chars = 30000  # Approximate - 1 token ≈ 4 chars
            if len(text) > max_chars:
                text = text[:max_chars]

            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )

            embedding = response.data[0].embedding
            self.stats['embeddings_generated'] += 1
            return embedding

        except Exception as e:
            print(f"  Error generating embedding: {e}")
            return None

    def save_law_with_articles_and_embeddings(
        self,
        law: Dict,
        folder_uuid: str
    ) -> Optional[str]:
        """Save law, articles, and generate embeddings in one transaction"""
        try:
            # Step 1: Save or update law
            existing = self.supabase.table('laws').select('id').eq('url', law['url']).maybeSingle().execute()

            law_data = {
                'name_ar': law['name_ar'],
                'url': law['url'],
                'folder_id': folder_uuid,
                'law_number': law.get('law_number', ''),
                'publication_date': law.get('publication_date'),
                'full_text_ar': law.get('full_text_ar', ''),
                'metadata': law.get('metadata', {}),
                'last_checked_at': datetime.now().isoformat()
            }

            if existing.data:
                law_uuid = existing.data['id']
                self.supabase.table('laws').update(law_data).eq('id', law_uuid).execute()
                print(f"  Updated law in database")

                # Delete old articles and embeddings for clean re-insert
                self.supabase.table('law_articles').delete().eq('law_id', law_uuid).execute()
                self.supabase.table('law_embeddings').delete().eq('law_id', law_uuid).execute()
            else:
                result = self.supabase.table('laws').insert(law_data).execute()
                law_uuid = result.data[0]['id'] if result.data else None
                print(f"  Inserted law into database")

            if not law_uuid:
                return None

            # Step 2: Save articles
            articles = law.get('articles', [])
            if articles:
                for article in articles:
                    article_data = {
                        'law_id': law_uuid,
                        'article_number': article['article_number'],
                        'article_title_ar': article.get('article_title_ar', ''),
                        'article_text_ar': article['article_text_ar']
                    }

                    result = self.supabase.table('law_articles').insert(article_data).execute()

                    if result.data:
                        article_id = result.data[0]['id']

                        # Step 3: Generate and save embedding for this article
                        if self.has_openai:
                            # Combine article info for better semantic search
                            embedding_text = f"المادة {article['article_number']}"
                            if article.get('article_title_ar'):
                                embedding_text += f": {article['article_title_ar']}\n"
                            embedding_text += article['article_text_ar']

                            embedding = self.generate_embedding(embedding_text)

                            if embedding:
                                embedding_data = {
                                    'law_id': law_uuid,
                                    'article_id': article_id,
                                    'embedding': embedding,
                                    'text_chunk': embedding_text,
                                    'chunk_index': int(article['article_number']) if article['article_number'].isdigit() else 0
                                }

                                self.supabase.table('law_embeddings').insert(embedding_data).execute()

                            # Rate limiting - avoid OpenAI rate limits
                            time.sleep(0.1)

                print(f"  Saved {len(articles)} articles with embeddings")

            return law_uuid

        except Exception as e:
            print(f"  Error saving law with articles: {e}")
            self.stats['errors'].append({'url': law.get('url', 'unknown'), 'error': str(e)})
            return None

    def scrape_folders(self) -> List[Dict]:
        """Scrape all law folders"""
        print(f"Fetching folders from: {self.folders_url}")

        try:
            response = self.fetcher.fetch(self.folders_url)

            if not response or response.status != 200:
                print(f"Failed to fetch folders. Status: {response.status if response else 'None'}")
                return []

            folders = []
            folder_elements = response.css('a[href*="/BoeLaws/Laws/Folders/"]').getall()

            for element in folder_elements:
                try:
                    href = element.attrib.get('href', '')
                    if not href or href == self.folders_url:
                        continue

                    folder_id = href.split('/')[-1] if '/' in href else ''

                    if href.startswith('/'):
                        url = f"{self.base_url}{href}"
                    elif not href.startswith('http'):
                        url = f"{self.folders_url}/{href}"
                    else:
                        url = href

                    name_ar = self.clean_text(element.text)

                    if name_ar and folder_id:
                        folders.append({
                            'folder_id': folder_id,
                            'name_ar': name_ar,
                            'name_en': '',
                            'url': url
                        })

                except Exception as e:
                    print(f"Error processing folder: {e}")
                    continue

            print(f"Found {len(folders)} folders")
            return folders

        except Exception as e:
            print(f"Error scraping folders: {e}")
            self.stats['errors'].append({'location': 'folders', 'error': str(e)})
            return []

    def scrape_laws_from_folder(self, folder_url: str) -> List[Dict]:
        """Scrape all laws from a folder"""
        print(f"  Fetching laws from folder")

        try:
            response = self.fetcher.fetch(folder_url)

            if not response or response.status != 200:
                return []

            laws = []
            law_elements = response.css('a[href*="/LawDetails/"]').getall()

            for element in law_elements:
                try:
                    href = element.attrib.get('href', '')
                    if not href:
                        continue

                    if href.startswith('/'):
                        url = f"{self.base_url}{href}"
                    elif not href.startswith('http'):
                        url = f"{self.base_url}{href}"
                    else:
                        url = href

                    name_ar = self.clean_text(element.text)

                    if name_ar:
                        laws.append({
                            'name_ar': name_ar,
                            'url': url
                        })

                except Exception as e:
                    print(f"  Error processing law link: {e}")
                    continue

            print(f"  Found {len(laws)} laws")
            return laws

        except Exception as e:
            print(f"  Error scraping laws: {e}")
            return []

    def save_folder(self, folder: Dict) -> Optional[str]:
        """Save folder to database"""
        try:
            existing = self.supabase.table('law_folders').select('id').eq('folder_id', folder['folder_id']).maybeSingle().execute()

            if existing.data:
                folder_uuid = existing.data['id']
                self.supabase.table('law_folders').update(folder).eq('id', folder_uuid).execute()
            else:
                result = self.supabase.table('law_folders').insert(folder).execute()
                folder_uuid = result.data[0]['id'] if result.data else None

            return folder_uuid

        except Exception as e:
            print(f"Error saving folder: {e}")
            return None

    def save_checkpoint(self, checkpoint_data: Dict):
        """Save progress checkpoint"""
        try:
            with open('scraper_checkpoint.json', 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving checkpoint: {e}")

    def load_checkpoint(self) -> Optional[Dict]:
        """Load progress checkpoint"""
        try:
            if os.path.exists('scraper_checkpoint.json'):
                with open('scraper_checkpoint.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
        return None

    def run_complete_scrape(self):
        """Run the complete scraping process"""
        print("=" * 80)
        print("ENHANCED SAUDI LAW SCRAPER - COMPLETE DATABASE POPULATION")
        print("=" * 80)
        print(f"Start time: {datetime.now()}")
        print()

        # Check for checkpoint
        checkpoint = self.load_checkpoint()
        processed_folders = checkpoint.get('processed_folders', []) if checkpoint else []

        # Scrape folders
        folders = self.scrape_folders()

        if not folders:
            print("No folders found!")
            return

        # Process each folder
        for folder_idx, folder in enumerate(folders, 1):
            print(f"\n[{folder_idx}/{len(folders)}] Processing: {folder['name_ar']}")

            if folder['folder_id'] in processed_folders:
                print("  (Skipping - already processed)")
                continue

            # Save folder
            folder_uuid = self.save_folder(folder)
            if not folder_uuid:
                print("  Failed to save folder")
                continue

            self.stats['folders_processed'] += 1

            # Scrape laws from folder
            laws = self.scrape_laws_from_folder(folder['url'])

            # Process each law
            for law_idx, law in enumerate(laws, 1):
                print(f"\n  [{law_idx}/{len(laws)}] {law['name_ar'][:60]}...")

                # Scrape law details
                law_details = self.scrape_law_details(law['url'])

                if law_details:
                    law.update(law_details)

                    # Save law with articles and embeddings
                    self.save_law_with_articles_and_embeddings(law, folder_uuid)
                    self.stats['laws_processed'] += 1

                # Rate limiting
                time.sleep(1)

            # Save checkpoint after each folder
            processed_folders.append(folder['folder_id'])
            self.save_checkpoint({
                'processed_folders': processed_folders,
                'timestamp': datetime.now().isoformat(),
                'stats': self.stats
            })

            print(f"\n  Folder complete. Total stats so far:")
            print(f"    Laws: {self.stats['laws_processed']}")
            print(f"    Articles: {self.stats['articles_extracted']}")
            print(f"    Embeddings: {self.stats['embeddings_generated']}")

        # Final statistics
        print("\n" + "=" * 80)
        print("SCRAPING COMPLETED!")
        print("=" * 80)
        print(f"End time: {datetime.now()}")
        print(f"\nFinal Statistics:")
        print(f"  Folders processed: {self.stats['folders_processed']}")
        print(f"  Laws processed: {self.stats['laws_processed']}")
        print(f"  Articles extracted: {self.stats['articles_extracted']}")
        print(f"  Embeddings generated: {self.stats['embeddings_generated']}")
        print(f"  Errors encountered: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print(f"\nErrors (first 10):")
            for error in self.stats['errors'][:10]:
                print(f"  - {error}")

        # Save final stats
        with open('scraper_final_stats.json', 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

        print(f"\nDetailed stats saved to: scraper_final_stats.json")


def main():
    """Main entry point"""
    scraper = EnhancedLawScraper()
    scraper.run_complete_scrape()


if __name__ == '__main__':
    main()
