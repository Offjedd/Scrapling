# 🚀 Run the Enhanced Scraper

## Quick Start - Get ALL Laws

```bash
python3 enhanced_scraper.py
```

This single command will:
- ✅ Scrape ALL folders (recursive, multi-layer)
- ✅ Extract ALL laws from every folder
- ✅ Generate embeddings automatically
- ✅ Save everything to database
- ✅ Track progress

## What It Does

### 1. Multi-Layer Folder Crawling
```
📁 Root
  📁 Category 1
    📁 Subcategory 1.1
      📜 Law A ✅
      📜 Law B ✅
    📁 Subcategory 1.2
      📜 Law C ✅
  📁 Category 2
    📜 Law D ✅
  📁 Category 3
    📁 Deep nested folder
      📁 Even deeper
        📜 Law E ✅
```

**Every law gets found and processed!**

### 2. For Each Law:
- Extract full Arabic text
- Extract all articles
- Generate OpenAI embedding (1536 dimensions)
- Save to database with proper relationships
- Link to parent folder

### 3. Progress Tracking:
- Shows real-time progress
- Saves to `scrape_progress.json`
- Avoids duplicate scraping
- Can resume if interrupted

## Expected Output

```
================================================================================
🚀 Enhanced Saudi Law Scraper
================================================================================

📁 Scraping folder (level 0): https://laws.boe.gov.sa/BoeLaws/Laws/Folders/
  Found 15 subfolders
  ✅ Folder: الأنظمة الأساسية

  📁 Scraping folder (level 1): ...
    Found 5 laws

    [1/5] نظام العمل
      🧠 Generating embedding...
      ✅ Law saved
      ✅ Embedding saved
      ✅ 45 articles saved

    [2/5] نظام الشركات
      🧠 Generating embedding...
      ✅ Law saved
      ✅ Embedding saved
      ✅ 32 articles saved

...

================================================================================
📊 Scraping Summary
================================================================================
Total Folders: 23
Total Laws: 127
Time Elapsed: 1847.3 seconds
================================================================================

💾 Progress saved to: scrape_progress.json

================================================================================
💾 Saving to Database
================================================================================
...
```

## Performance

**Timing:**
- ~5-10 seconds per law (fetch + parse + embed + save)
- 50 laws = ~8-15 minutes
- 100 laws = ~15-30 minutes
- 200 laws = ~30-60 minutes

**API Usage:**
- OpenAI embeddings: $0.00002 per law (very cheap!)
- 100 laws = ~$0.002 (less than a penny!)

## What Gets Saved

### Database Tables Populated:

1. **law_folders**
   - All folder hierarchy
   - Multi-level structure preserved

2. **laws**
   - Full law text
   - Law numbers
   - URLs for reference

3. **law_embeddings**
   - 1536-dimension vectors
   - Enables semantic search
   - Powers AI answers

4. **law_articles**
   - Individual articles
   - Article numbers
   - Granular search

## After Scraping

Your app will have:
- ✅ 50-200+ laws (depending on website)
- ✅ Vector embeddings for each law
- ✅ Full article-level data
- ✅ Fast semantic search
- ✅ Accurate AI responses

## Resume After Interruption

If the scraper stops, just run it again:

```bash
python3 enhanced_scraper.py
```

It automatically:
- Reads `scrape_progress.json`
- Skips already-visited URLs
- Continues from where it left off

## Check Progress

While running, check the database:

```bash
# Count laws
python3 << EOF
import requests
response = requests.get(
    "https://exilgibjcnrtashitzjk.supabase.co/rest/v1/laws?select=count",
    headers={"apikey": "YOUR_ANON_KEY"}
)
print(f"Laws in database: {response.json()}")
EOF
```

## Troubleshooting

**Problem: Slow scraping**
- This is normal! Polite scraping + embedding generation takes time
- Each law needs: fetch (2s) + parse (1s) + embed (3s) + save (2s) = ~8s

**Problem: OpenAI errors**
- Check `OPENAI_API_KEY` in `.env`
- Verify you have credits: https://platform.openai.com/usage

**Problem: Supabase errors**
- Check `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env`
- Verify database migrations applied

**Problem: Network errors**
- Scraper will skip failed pages
- Check `scrape_progress.json` for details
- Run again to retry

## Monitoring

Watch the console output:
- ✅ = Success
- ⚠️ = Warning (non-fatal)
- ❌ = Error (skipped)

## After Completion

1. **Test the data:**
   ```bash
   python3 test_system.py
   ```

2. **Start the app:**
   ```bash
   npm run dev
   ```

3. **Ask questions:**
   - Open http://localhost:5173
   - Try: "ما هي ساعات العمل القانونية؟"
   - Should get accurate answer with citations!

## Files Created

- `scrape_progress.json` - Full scraping results (backup)
- Console logs - Real-time progress
- Database - All laws with embeddings

## Next Steps

After scraping completes:
1. ✅ You have 50-200+ laws with embeddings
2. ✅ AI can answer complex legal questions
3. ✅ Fast semantic search enabled
4. ✅ Complete citation system working

**Your Saudi Law AI is now FULLY POWERED!** 🎉

## Schedule Regular Updates

To keep laws updated, run weekly:

```bash
# Add to crontab
0 2 * * 0 cd /path/to/project && python3 enhanced_scraper.py
```

This ensures your database stays current with the latest laws!
