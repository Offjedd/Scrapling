#!/usr/bin/env python3
"""
Comprehensive Saudi Law Scraper
Scrapes all laws from laws.boe.gov.sa recursively
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from openai import OpenAI
from urllib.parse import urljoin
import re

# Load env
env = {}
with open('.env') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            env[key] = val

SUPABASE_URL = env['SUPABASE_URL']
SERVICE_KEY = env['SUPABASE_SERVICE_ROLE_KEY']
OPENAI_KEY = env['OPENAI_API_KEY']

headers_db = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

headers_web = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

openai_client = OpenAI(api_key=OPENAI_KEY)

visited_urls = set()
scraped_laws = []

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def scrape_law_page(url):
    """Scrape a single law page"""
    if url in visited_urls:
        return None

    visited_urls.add(url)

    try:
        print(f"  Fetching: {url}")
        resp = requests.get(url, headers=headers_web, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')

        # Extract law title
        title = soup.find('h1') or soup.find('h2') or soup.find('title')
        law_name = clean_text(title.get_text()) if title else "Unknown Law"

        # Extract law number from page or URL
        law_number_match = re.search(r'(?:رقم|م/|M/)([^\s\)]+)', law_name)
        law_number = law_number_match.group(1) if law_number_match else ""

        # Extract all text content
        content_divs = soup.find_all(['div', 'article', 'section', 'p'])
        full_text = '\n'.join([clean_text(div.get_text()) for div in content_divs if div.get_text()])

        # Limit text length
        full_text = full_text[:10000]

        if len(full_text) < 100:
            print(f"    ⚠️  Too short, skipping")
            return None

        law_data = {
            'name_ar': law_name[:500],
            'law_number': law_number[:50],
            'full_text_ar': full_text,
            'url': url
        }

        print(f"    ✅ Scraped: {law_name[:50]}...")
        return law_data

    except Exception as e:
        print(f"    ❌ Error: {str(e)[:100]}")
        return None

def scrape_folder(folder_url, depth=0, max_depth=3):
    """Recursively scrape a folder"""
    if depth > max_depth or folder_url in visited_urls:
        return

    visited_urls.add(folder_url)
    indent = "  " * depth

    print(f"{indent}📁 Folder (depth {depth}): {folder_url}")

    try:
        resp = requests.get(folder_url, headers=headers_web, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')

        # Find all links
        links = soup.find_all('a', href=True)

        folder_links = []
        law_links = []

        for link in links:
            href = link['href']
            full_url = urljoin('https://laws.boe.gov.sa', href)

            # Categorize links
            if '/Folders/' in href and full_url not in visited_urls:
                folder_links.append(full_url)
            elif '/LawDetails/' in href and full_url not in visited_urls:
                law_links.append(full_url)

        print(f"{indent}  Found: {len(folder_links)} folders, {len(law_links)} laws")

        # Scrape laws in this folder
        for law_url in law_links:
            law_data = scrape_law_page(law_url)
            if law_data:
                scraped_laws.append(law_data)
            time.sleep(1)  # Be respectful

        # Recurse into subfolders
        for subfolder_url in folder_links:
            scrape_folder(subfolder_url, depth + 1, max_depth)
            time.sleep(1)

    except Exception as e:
        print(f"{indent}  ❌ Folder error: {str(e)[:100]}")

def save_to_database(laws):
    """Save laws to database with embeddings"""
    print(f"\n💾 Saving {len(laws)} laws to database...")

    saved_count = 0

    for i, law in enumerate(laws, 1):
        print(f"\n[{i}/{len(laws)}] {law['name_ar'][:50]}...")

        try:
            # Check if already exists
            check_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/laws?url=eq.{law['url']}&select=id",
                headers=headers_db,
                timeout=30
            )

            if check_resp.status_code == 200 and check_resp.json():
                print(f"  ⏭️  Already exists")
                continue

            # Insert law
            law_resp = requests.post(
                f"{SUPABASE_URL}/rest/v1/laws",
                headers=headers_db,
                json=law,
                timeout=30
            )

            if law_resp.status_code not in [200, 201]:
                print(f"  ❌ Insert failed: {law_resp.status_code}")
                continue

            law_id = law_resp.json()[0]['id']
            print(f"  ✅ Law saved")

            # Generate embedding
            print(f"  🧠 Generating embedding...")
            text_for_emb = f"{law['name_ar']}\n\n{law['full_text_ar']}"

            emb_response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text_for_emb[:8000]
            )
            embedding = emb_response.data[0].embedding

            # Save embedding
            emb_resp = requests.post(
                f"{SUPABASE_URL}/rest/v1/law_embeddings",
                headers=headers_db,
                json={
                    'law_id': law_id,
                    'text_chunk': law['name_ar'][:500],
                    'embedding': embedding,
                    'chunk_index': 0
                },
                timeout=30
            )

            if emb_resp.status_code in [200, 201]:
                print(f"  ✅ Embedding saved")
                saved_count += 1

            time.sleep(0.7)  # Rate limiting

        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")

    return saved_count

def main():
    print("=" * 80)
    print("🚀 Comprehensive Saudi Law Scraper")
    print("=" * 80)

    start_url = "https://laws.boe.gov.sa/BoeLaws/Laws/Folders/"

    print(f"\n📥 Starting recursive scrape from: {start_url}\n")

    # Scrape all folders and laws
    scrape_folder(start_url, depth=0, max_depth=3)

    print(f"\n\n📊 Scraping Complete!")
    print(f"  Total laws scraped: {len(scraped_laws)}")
    print(f"  Total URLs visited: {len(visited_urls)}")

    # Save to JSON file
    with open('all_scraped_laws.json', 'w', encoding='utf-8') as f:
        json.dump(scraped_laws, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved to: all_scraped_laws.json")

    # Save to database
    if scraped_laws:
        saved = save_to_database(scraped_laws)
        print(f"\n✅ Successfully saved {saved} laws with embeddings to database!")
    else:
        print(f"\n⚠️  No laws scraped")

    print("\n" + "=" * 80)
    print("🎉 Done!")
    print("=" * 80)

if __name__ == '__main__':
    main()
