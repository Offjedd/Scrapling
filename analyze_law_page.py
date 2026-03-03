"""
Quick script to analyze the structure of a law page
"""
import requests
from bs4 import BeautifulSoup
import json

url = 'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/83431376-5cf3-4374-875a-a9a700f16985/1'

print(f"Fetching: {url}")
response = requests.get(url, timeout=30)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    print("\n=== Page Title ===")
    title = soup.find('title')
    if title:
        print(title.get_text(strip=True))

    print("\n=== Looking for 'نص النظام' section ===")
    # Find the law text section
    law_text_section = soup.find(string=lambda text: text and 'نص' in text and 'النظام' in text)
    if law_text_section:
        print(f"Found text: {law_text_section[:100]}")
        parent = law_text_section.parent
        print(f"Parent tag: {parent.name}")
        print(f"Parent classes: {parent.get('class', [])}")

    print("\n=== Looking for Articles (المادة) ===")
    # Find article elements
    articles = soup.find_all(string=lambda text: text and 'المادة' in text)
    print(f"Found {len(articles)} elements containing 'المادة'")
    for i, article in enumerate(articles[:5]):
        print(f"\nArticle {i+1}:")
        print(f"  Text: {str(article)[:100]}")
        parent = article.parent
        print(f"  Parent: {parent.name}, classes: {parent.get('class', [])}")

    print("\n=== All divs with classes ===")
    divs = soup.find_all('div', class_=True)
    classes_found = set()
    for div in divs:
        classes = div.get('class', [])
        for cls in classes:
            classes_found.add(cls)

    print(f"Unique classes found: {sorted(list(classes_found))[:20]}")

    print("\n=== Saving full HTML for inspection ===")
    with open('sample_law_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("Saved to sample_law_page.html")

else:
    print(f"Failed to fetch page: {response.status_code}")
