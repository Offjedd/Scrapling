#!/usr/bin/env python3
"""
Simple Saudi Law Scraper - Quick data population
Uses requests + BeautifulSoup for maximum compatibility
"""

import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from typing import List, Dict, Optional, Set

class SimpleLawScraper:
    def __init__(self):
        self.load_env()
        self.openai_client = OpenAI(api_key=self.openai_key)
        self.base_url = "https://laws.boe.gov.sa"
        self.visited = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def load_env(self):
        env = {}
        with open('.env') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    env[key] = val

        self.supabase_url = env['SUPABASE_URL']
        self.supabase_key = env['SUPABASE_SERVICE_ROLE_KEY']
        self.openai_key = env['OPENAI_API_KEY']

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def fetch_page(self, url: str):
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            return BeautifulSoup(resp.content, 'html.parser')
        except Exception as e:
            print(f"  ❌ Error fetching {url}: {e}")
            return None

    def generate_embedding(self, text: str) -> List[float]:
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"  ⚠️ Embedding error: {e}")
            return None

    def scrape_folders(self, url: str, level: int = 0) -> List[Dict]:
        if url in self.visited or level > 5:
            return []

        self.visited.add(url)
        indent = "  " * level
        print(f"{indent}📁 Level {level}: {url}")

        soup = self.fetch_page(url)
        if not soup:
            return []

        results = []

        # Find all links
        links = soup.find_all('a', href=True)

        folders = []
        laws = []

        for link in links:
            href = link['href']
            text = self.clean_text(link.get_text())

            if not text or not href:
                continue

            # Make absolute URL
            if href.startswith('/'):
                full_url = f"{self.base_url}{href}"
            elif not href.startswith('http'):
                full_url = f"{self.base_url}/{href}"
            else:
                full_url = href

            # Classify as folder or law
            if '/Folders/' in href and full_url not in self.visited:
                folders.append({'url': full_url, 'name': text})
            elif '/Laws/' in href and '/Folders/' not in href and full_url not in self.visited:
                laws.append({'url': full_url, 'name': text})

        print(f"{indent}  Found: {len(folders)} folders, {len(laws)} laws")

        # Process laws first
        for law in laws[:10]:  # Limit to 10 laws per folder for speed
            law_data = self.scrape_law(law['url'], law['name'], level)
            if law_data:
                results.append(law_data)
                time.sleep(2)

        # Recurse into folders
        for folder in folders[:5]:  # Limit to 5 subfolders for speed
            sub_results = self.scrape_folders(folder['url'], level + 1)
            results.extend(sub_results)
            time.sleep(1)

        return results

    def scrape_law(self, url: str, name: str, level: int) -> Optional[Dict]:
        indent = "  " * (level + 1)
        print(f"{indent}📜 {name}")

        self.visited.add(url)

        soup = self.fetch_page(url)
        if not soup:
            return None

        # Extract all text
        text_elements = soup.find_all(['p', 'div', 'article', 'section'])
        full_text = ' '.join([self.clean_text(elem.get_text()) for elem in text_elements])

        if not full_text or len(full_text) < 50:
            # Fallback to body
            body = soup.find('body')
            if body:
                full_text = self.clean_text(body.get_text())

        # Extract articles
        articles = []
        article_pattern = r'(?:المادة|مادة)\s+([^\n:]{1,20})[:\n]([^\n]+(?:\n(?!(?:المادة|مادة))[^\n]+)*)'
        matches = re.findall(article_pattern, full_text[:10000], re.MULTILINE)

        for i, (number, text) in enumerate(matches[:20]):
            articles.append({
                'number': self.clean_text(number),
                'text': self.clean_text(text)
            })

        return {
            'name': name,
            'url': url,
            'text': full_text[:5000],
            'articles': articles
        }

    def save_to_database(self, laws: List[Dict]):
        print(f"\n💾 Saving {len(laws)} laws to database...")

        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

        saved_count = 0

        for i, law in enumerate(laws, 1):
            try:
                print(f"\n[{i}/{len(laws)}] {law['name']}")

                # Insert law
                law_response = requests.post(
                    f"{self.supabase_url}/rest/v1/laws",
                    headers=headers,
                    json={
                        'name_ar': law['name'],
                        'url': law['url'],
                        'full_text_ar': law['text'],
                        'law_number': ''
                    },
                    timeout=30
                )

                if law_response.status_code not in [200, 201]:
                    print(f"  ⚠️ Skip (may exist): {law_response.status_code}")
                    continue

                law_data = law_response.json()
                law_id = law_data[0]['id'] if isinstance(law_data, list) else law_data['id']
                print(f"  ✅ Law saved")

                # Generate and save embedding
                print(f"  🧠 Generating embedding...")
                text_for_emb = f"{law['name']}\n\n{law['text']}"
                embedding = self.generate_embedding(text_for_emb)

                if embedding:
                    emb_response = requests.post(
                        f"{self.supabase_url}/rest/v1/law_embeddings",
                        headers=headers,
                        json={
                            'law_id': law_id,
                            'text_chunk': law['name'],
                            'embedding': embedding,
                            'chunk_index': 0
                        },
                        timeout=30
                    )

                    if emb_response.status_code in [200, 201]:
                        print(f"  ✅ Embedding saved")
                        saved_count += 1

                # Save articles
                for article in law['articles'][:10]:
                    try:
                        requests.post(
                            f"{self.supabase_url}/rest/v1/law_articles",
                            headers=headers,
                            json={
                                'law_id': law_id,
                                'article_number': article['number'],
                                'article_text_ar': article['text']
                            },
                            timeout=30
                        )
                    except:
                        pass

                if law['articles']:
                    print(f"  ✅ {len(law['articles'])} articles")

                time.sleep(1)

            except Exception as e:
                print(f"  ❌ Error: {e}")

        return saved_count

    def run(self):
        print("=" * 80)
        print("🚀 Simple Saudi Law Scraper")
        print("=" * 80)

        start_url = "https://laws.boe.gov.sa/BoeLaws/Laws/Folders/"

        print("\n📥 Starting scrape...")
        laws = self.scrape_folders(start_url)

        print(f"\n\n📊 Scraped {len(laws)} laws")

        # Save to file
        with open('scraped_laws.json', 'w', encoding='utf-8') as f:
            json.dump(laws, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved to scraped_laws.json")

        # Save to database
        saved = self.save_to_database(laws)

        print("\n" + "=" * 80)
        print(f"✅ Complete! Saved {saved} laws with embeddings")
        print("=" * 80)

if __name__ == '__main__':
    scraper = SimpleLawScraper()
    scraper.run()
