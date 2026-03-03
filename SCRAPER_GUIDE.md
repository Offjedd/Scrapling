# Enhanced Saudi Law Scraper - Complete Guide

## Overview

The Enhanced Saudi Law Scraper (`enhanced_law_scraper.py`) is a comprehensive tool that scrapes the complete Saudi Law database from https://laws.boe.gov.sa/ and populates your Supabase database with:

- **Folders**: All law categories and hierarchies
- **Laws**: Complete law metadata (name, number, publication date, full text)
- **Articles**: Individual articles extracted from each law (المادة الأولى, المادة الثانية, etc.)
- **Embeddings**: Vector embeddings for each article enabling semantic search

## Features

### 1. Complete Data Extraction
- Scrapes all law folders from the main page
- Extracts every law from each folder
- Parses individual articles from law text
- Handles Arabic text properly with normalization

### 2. Article-Level Processing
- Identifies article boundaries using multiple patterns
- Extracts article numbers (converts Arabic words to digits)
- Captures article titles when present
- Stores each article as a separate database record

### 3. Semantic Search Support
- Generates OpenAI embeddings for each article
- Stores embeddings in vector format
- Enables precise article-level search (not just law-level)

### 4. Robust Error Handling
- Checkpoint system to resume interrupted scrapes
- Detailed error logging
- Rate limiting to avoid server blocks
- Retry logic for failed requests

### 5. Progress Tracking
- Real-time statistics display
- Checkpoint files for resuming
- Final statistics report
- Error summary

## Prerequisites

### Required Environment Variables

Ensure your `.env` file contains:

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key  # For embeddings
```

### Required Python Packages

```bash
pip install supabase openai python-dotenv scrapling
```

## Usage

### Basic Usage

Run the complete scraper:

```bash
python enhanced_law_scraper.py
```

This will:
1. Scrape all folders from the main page
2. For each folder, scrape all laws
3. For each law, extract all articles
4. Generate embeddings for each article
5. Save everything to Supabase database

### Resume from Checkpoint

If the scraper is interrupted, it will automatically resume from the last completed folder:

```bash
python enhanced_law_scraper.py
```

The checkpoint file (`scraper_checkpoint.json`) tracks progress.

### Start Fresh

To start from the beginning, delete the checkpoint file:

```bash
rm scraper_checkpoint.json
python enhanced_law_scraper.py
```

## Output Files

### 1. scraper_checkpoint.json
- Tracks which folders have been processed
- Allows resuming interrupted scrapes
- Updates after each folder completion

### 2. scraper_final_stats.json
- Complete statistics from the scraping run
- Includes error details
- Generated at the end of scraping

## Expected Output

### Console Output

```
================================================================================
ENHANCED SAUDI LAW SCRAPER - COMPLETE DATABASE POPULATION
================================================================================
Start time: 2026-03-03 10:30:00

Fetching folders from: https://laws.boe.gov.sa/BoeLaws/Laws/Folders/
Found 25 folders

[1/25] Processing: الأنظمة الأساسية
  Found 15 laws

  [1/15] نظام الإجازة الأساسي...
  Fetching: https://laws.boe.gov.sa/...
  Extracted 12 articles
  Updated law in database
  Saved 12 articles with embeddings

  [2/15] نظام المرور...
  ...

  Folder complete. Total stats so far:
    Laws: 15
    Articles: 180
    Embeddings: 180

[2/25] Processing: الأنظمة التجارية
  ...

================================================================================
SCRAPING COMPLETED!
================================================================================
End time: 2026-03-03 12:45:00

Final Statistics:
  Folders processed: 25
  Laws processed: 487
  Articles extracted: 5,832
  Embeddings generated: 5,832
  Errors encountered: 3
```

## Database Schema

### Tables Populated

1. **law_folders**
   - `id` (UUID)
   - `folder_id` (text) - Original folder ID from website
   - `name_ar` (text) - Arabic folder name
   - `url` (text) - Folder URL

2. **laws**
   - `id` (UUID)
   - `folder_id` (UUID) - Foreign key to law_folders
   - `law_number` (text)
   - `name_ar` (text) - Law name in Arabic
   - `publication_date` (date)
   - `full_text_ar` (text) - Complete law text
   - `url` (text) - Law page URL
   - `metadata` (jsonb) - Additional metadata

3. **law_articles**
   - `id` (UUID)
   - `law_id` (UUID) - Foreign key to laws
   - `article_number` (text) - e.g., "1", "2", "3"
   - `article_title_ar` (text) - Article title if present
   - `article_text_ar` (text) - Article content

4. **law_embeddings**
   - `id` (UUID)
   - `law_id` (UUID) - Foreign key to laws
   - `article_id` (UUID) - Foreign key to law_articles
   - `embedding` (vector) - OpenAI embedding vector
   - `text_chunk` (text) - The text that was embedded
   - `chunk_index` (integer) - Article number for ordering

## Article Extraction Logic

The scraper uses multiple strategies to extract articles:

### Pattern Recognition

Identifies articles using these patterns:
- `المادة الأولى` (Article the First)
- `المادة (1)` (Article (1))
- `المادة 1` (Article 1)
- `مادة 1` (Article 1 - alternative form)

### Normalization

- Converts Arabic number words to digits (الأولى → 1)
- Normalizes Arabic-Indic digits (٠-٩) to Western (0-9)
- Cleans whitespace and special characters

### Content Extraction

- Captures everything between article markers
- Extracts optional article titles
- Preserves complete article text

## Troubleshooting

### Issue: No articles extracted

**Cause**: The law page structure might be different
**Solution**: The scraper will fall back to full text storage. Articles can be manually split later.

### Issue: Embeddings not generated

**Cause**: Missing or invalid OPENAI_API_KEY
**Solution**: Check your .env file has the correct API key

### Issue: Rate limiting errors

**Cause**: Too many requests to OpenAI API
**Solution**: The scraper includes automatic rate limiting (0.1s between embeddings)

### Issue: Network timeout

**Cause**: Server is slow or unreachable
**Solution**: The scraper will retry. If it fails, it will log the error and continue with other laws.

### Issue: Checkpoint not working

**Cause**: Checkpoint file is corrupted
**Solution**: Delete `scraper_checkpoint.json` and restart

## Performance

### Speed
- ~1-2 seconds per law (including network delay)
- ~0.1 seconds per embedding generation
- Complete database: 2-4 hours for ~500 laws

### Rate Limiting
- 1 second delay between law requests
- 0.1 second delay between embedding requests
- Respects server load

### Resource Usage
- Memory: ~200-500 MB
- Network: ~50-100 MB total
- Disk: ~10 MB for checkpoint and stats files

## Best Practices

1. **Run in a stable environment**: Use a server or stable connection
2. **Monitor progress**: Watch the console output for errors
3. **Check statistics**: Review final stats to ensure completeness
4. **Validate data**: Run validation queries after completion
5. **Backup before re-running**: The scraper will update existing records

## Validation Queries

After scraping, run these queries to validate data:

```sql
-- Check total counts
SELECT
  (SELECT COUNT(*) FROM law_folders) as folders,
  (SELECT COUNT(*) FROM laws) as laws,
  (SELECT COUNT(*) FROM law_articles) as articles,
  (SELECT COUNT(*) FROM law_embeddings) as embeddings;

-- Find laws without articles
SELECT id, name_ar
FROM laws
WHERE id NOT IN (SELECT DISTINCT law_id FROM law_articles);

-- Check average articles per law
SELECT AVG(article_count) as avg_articles
FROM (
  SELECT law_id, COUNT(*) as article_count
  FROM law_articles
  GROUP BY law_id
) subquery;

-- Find articles without embeddings
SELECT COUNT(*)
FROM law_articles
WHERE id NOT IN (SELECT DISTINCT article_id FROM law_embeddings WHERE article_id IS NOT NULL);
```

## Next Steps

After successful scraping:

1. **Test Search Functionality**: Use the query-law Edge Function to test semantic search
2. **Build Frontend**: Create a search interface for users
3. **Schedule Updates**: Set up daily/weekly runs to catch law updates
4. **Optimize Search**: Fine-tune vector search parameters for best results

## Support

For issues or questions:
- Check the error logs in `scraper_final_stats.json`
- Review the checkpoint file for progress details
- Examine database records for specific laws that failed
