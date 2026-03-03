# Complete Saudi Law AI System - Setup & Usage Guide

## Overview

This is a complete AI-powered Saudi law search system that provides semantic search across Saudi Arabian legal documents at the article level. The system includes:

- **Enhanced Web Scraper**: Extracts law folders, laws, and individual articles from laws.boe.gov.sa
- **Vector Embeddings**: Generates OpenAI embeddings for each article for semantic search
- **Article-Level Search**: Precise search that returns specific articles, not just entire laws
- **Beautiful Frontend**: Modern, RTL-optimized interface in Arabic
- **Edge Functions**: Serverless functions for query processing
- **Complete Database**: Supabase with RLS, vector search, and audit logging

---

## System Architecture

```
User Query (Arabic)
    ↓
Frontend (Vite + JavaScript)
    ↓
Edge Function (query-law)
    ↓
OpenAI (Generate Query Embedding)
    ↓
Supabase Vector Search (Article-Level)
    ↓
OpenAI GPT-4 (Generate Answer)
    ↓
Response with Citations
    ↓
Display to User
```

---

## Prerequisites

### 1. Environment Variables

Create a `.env` file with:

```bash
# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Frontend (for Vite)
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

### 2. Required Packages

Python packages:
```bash
pip install supabase openai python-dotenv scrapling beautifulsoup4 requests
```

Node packages (already installed):
```bash
npm install
```

---

## Step 1: Database Setup

### Check Current Database Status

Run the validation script to see what's in the database:

```bash
python validate_database.py
```

This will show:
- Total counts of folders, laws, articles, and embeddings
- Laws without articles
- Articles without embeddings
- Data quality issues
- Health score

**Current Status**: You have 9 sample laws with embeddings but NO articles extracted.

---

## Step 2: Populate Database with Complete Law Data

### Run the Enhanced Scraper

The enhanced scraper will:
1. Scrape all law folders from laws.boe.gov.sa
2. Extract all laws from each folder
3. Parse each law page to extract individual articles
4. Generate OpenAI embeddings for each article
5. Save everything to Supabase

**To run the scraper:**

```bash
python enhanced_law_scraper.py
```

### What to Expect

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
```

### Scraper Features

- **Checkpoint System**: Automatically saves progress after each folder
- **Resume Capability**: If interrupted, restart the script and it will continue from the last folder
- **Error Handling**: Logs errors but continues with other laws
- **Rate Limiting**: Includes delays to avoid overwhelming the server
- **Statistics**: Generates detailed statistics at the end

### Expected Results

- **Time**: 2-4 hours for complete database (~500 laws)
- **Folders**: ~20-30 law categories
- **Laws**: ~400-600 laws
- **Articles**: ~5,000-10,000 individual articles
- **Embeddings**: One per article

### Output Files

- `scraper_checkpoint.json` - Progress checkpoint
- `scraper_final_stats.json` - Complete statistics
- Console output with real-time progress

---

## Step 3: Validate Database Completeness

After scraping completes, validate the data:

```bash
python validate_database.py
```

### What to Check

1. **Basic Counts**: Should have hundreds of laws and thousands of articles
2. **Laws without Articles**: Should be minimal (some PDFs may not parse)
3. **Articles without Embeddings**: Should be 0 (or fix with script)
4. **Data Quality**: No major issues reported
5. **Health Score**: Should be 90-100

### If Issues Found

**Missing Articles**: Some laws may have unstructured PDFs
- Manually review these laws
- Consider manual article extraction

**Missing Embeddings**: Run embedding generation separately
```bash
python generate_embeddings.py  # If you create this script
```

---

## Step 4: Deploy and Test

### Deploy Edge Functions (Already Done)

The `query-law` Edge Function has been deployed and is ready to use.

### Start Development Server

```bash
npm run dev
```

Access the application at: `http://localhost:5173`

### Test the Search

Try these sample queries:

**Arabic Queries:**
- ما هي ساعات العمل القانونية؟
- ما هي حقوق العامل في الإجازات؟
- ماذا يقول النظام عن عقوبات المرور؟
- ما هي شروط الزواج في النظام السعودي؟

**What You Should See:**
- User query displayed
- AI response with relevant information
- Citations showing:
  - Law name
  - Article number
  - Source link

---

## Step 5: Production Deployment

### Build for Production

```bash
npm run build
```

### Deploy Frontend

The `dist` folder contains the production build. Deploy to:
- Vercel
- Netlify
- Cloudflare Pages
- Or any static hosting service

**Environment Variables**: Make sure to set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` in your hosting platform.

### Monitor Edge Functions

View logs in Supabase Dashboard:
1. Go to Edge Functions section
2. Select `query-law`
3. View logs and invocations

---

## Database Schema

### Tables

#### 1. law_folders
Stores law categories and hierarchies.

```sql
CREATE TABLE law_folders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  folder_id text UNIQUE NOT NULL,
  name_ar text NOT NULL,
  name_en text DEFAULT '',
  url text NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
```

#### 2. laws
Stores complete law information.

```sql
CREATE TABLE laws (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  folder_id uuid REFERENCES law_folders(id),
  law_number text DEFAULT '',
  name_ar text NOT NULL,
  name_en text DEFAULT '',
  publication_date date,
  url text UNIQUE NOT NULL,
  full_text_ar text DEFAULT '',
  full_text_en text DEFAULT '',
  metadata jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  last_checked_at timestamptz DEFAULT now()
);
```

#### 3. law_articles
Stores individual articles from each law.

```sql
CREATE TABLE law_articles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  law_id uuid REFERENCES laws(id) NOT NULL,
  article_number text NOT NULL,
  article_title_ar text DEFAULT '',
  article_text_ar text NOT NULL,
  article_text_en text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
```

#### 4. law_embeddings
Stores vector embeddings for semantic search.

```sql
CREATE TABLE law_embeddings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  law_id uuid REFERENCES laws(id) NOT NULL,
  article_id uuid REFERENCES law_articles(id),
  embedding vector(1536),
  text_chunk text NOT NULL,
  chunk_index integer DEFAULT 0,
  created_at timestamptz DEFAULT now()
);
```

#### 5. query_logs
Audit log of user queries.

```sql
CREATE TABLE query_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  query_text text NOT NULL,
  query_language text DEFAULT 'ar',
  response_text text,
  cited_articles jsonb DEFAULT '[]',
  response_time_ms integer DEFAULT 0,
  created_at timestamptz DEFAULT now()
);
```

### Key Functions

#### search_similar_articles
Article-level vector search function.

```sql
SELECT * FROM search_similar_articles(
  query_embedding := '[0.1, 0.2, ...]'::vector(1536),
  match_threshold := 0.3,
  match_count := 10
);
```

Returns:
- article_id
- law_id
- law_name_ar
- article_number
- article_text_ar
- similarity score

---

## Maintenance

### Daily Updates

Run the scraper in update mode to check for law changes:

```bash
python saudi_law_scraper.py update
```

This will:
- Check all laws for publication date changes
- Re-scrape and update changed laws
- Update articles and embeddings

### Monitor Query Performance

Check query logs:

```sql
SELECT
  query_text,
  response_time_ms,
  cited_articles,
  created_at
FROM query_logs
ORDER BY created_at DESC
LIMIT 20;
```

### Database Statistics

```sql
-- Total counts
SELECT
  (SELECT COUNT(*) FROM law_folders) as folders,
  (SELECT COUNT(*) FROM laws) as laws,
  (SELECT COUNT(*) FROM law_articles) as articles,
  (SELECT COUNT(*) FROM law_embeddings) as embeddings,
  (SELECT COUNT(*) FROM query_logs) as queries;

-- Average response time
SELECT AVG(response_time_ms) as avg_response_ms
FROM query_logs;

-- Most common queries
SELECT query_text, COUNT(*) as frequency
FROM query_logs
GROUP BY query_text
ORDER BY frequency DESC
LIMIT 10;
```

---

## Troubleshooting

### Issue: Scraper fails to connect

**Solution**: Check your internet connection and verify the website is accessible.

### Issue: No articles extracted

**Solution**: The law pages may have changed structure. Check the CSS selectors in the scraper.

### Issue: Embeddings not generating

**Solution**:
1. Verify OPENAI_API_KEY is set correctly
2. Check OpenAI API quota
3. Look for rate limit errors in logs

### Issue: Search returns no results

**Solution**:
1. Check if embeddings table has data
2. Verify the vector search function exists
3. Lower the match_threshold (try 0.2 instead of 0.3)

### Issue: Frontend shows connection error

**Solution**:
1. Verify VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
2. Check Edge Function is deployed
3. Check browser console for CORS errors

---

## Performance Optimization

### 1. Database Indexes

Already created:
- Vector index on law_embeddings.embedding
- B-tree indexes on foreign keys

### 2. Edge Function Optimization

- Uses connection pooling
- Caches database client
- Efficient vector search with LIMIT

### 3. Frontend Optimization

- Lazy loading
- Debounced search input
- Optimized bundle size

---

## Security

### Row Level Security (RLS)

All tables have RLS enabled with restrictive policies:

```sql
-- Public read access to laws (no authentication required)
CREATE POLICY "Public read access to laws"
  ON laws FOR SELECT
  TO anon
  USING (true);

-- Similar policies for articles and embeddings
```

### API Key Security

- Never expose SUPABASE_SERVICE_ROLE_KEY in frontend
- Use SUPABASE_ANON_KEY in frontend (limited permissions)
- OpenAI key only used in Edge Functions (server-side)

---

## Cost Estimation

### OpenAI Costs

- Embeddings: ~$0.02 per 1,000 articles
- GPT-4 queries: ~$0.03 per query
- For 10,000 articles: ~$0.20 initial + $0.03 per user query

### Supabase Costs

- Free tier: Up to 500MB database, 2GB bandwidth
- Pro tier: $25/month for larger databases
- Vector search is included

---

## Next Steps

1. **Run the Enhanced Scraper**: `python enhanced_law_scraper.py`
2. **Validate Results**: `python validate_database.py`
3. **Test Search**: `npm run dev` and try queries
4. **Deploy to Production**: `npm run build` and deploy
5. **Monitor Performance**: Check query logs and response times
6. **Schedule Updates**: Set up daily scraper runs for law updates

---

## Support & Documentation

- **Scraper Guide**: `SCRAPER_GUIDE.md` - Detailed scraper documentation
- **Validation Script**: `validate_database.py` - Check database health
- **Edge Function**: `supabase/functions/query-law/` - Query processing logic
- **Frontend**: `src/` - Application interface

---

## Summary

You now have a complete, production-ready Saudi Law AI system with:

✅ Enhanced web scraper with article extraction
✅ Vector embeddings for semantic search
✅ Article-level search (not just law-level)
✅ Modern, beautiful Arabic interface
✅ Deployed Edge Functions
✅ Complete database schema with RLS
✅ Validation and monitoring tools
✅ Checkpoint and resume capability
✅ Comprehensive documentation

**Next Action**: Run `python enhanced_law_scraper.py` to populate the database with complete law data!
