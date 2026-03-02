# Saudi Arabian Law AI Assistant
## مساعد الأنظمة السعودية الذكي

A comprehensive AI-powered system to answer questions about Saudi Arabian laws using web scraping, vector embeddings, and large language models.

## 🌟 Features

- **Automatic Law Scraping**: Uses Scrapling library to extract laws from https://laws.boe.gov.sa/BoeLaws/Laws/Folders/
- **Arabic-Optimized AI**: Provides accurate answers in both Arabic and English
- **Semantic Search**: Vector embeddings enable intelligent understanding of legal queries
- **Complete Citations**: Every answer includes law name, article number, publication date, and URL
- **Daily Updates**: Automatically checks for law changes based on publication dates
- **Web Interface**: Beautiful, responsive interface for testing the system

## 📋 System Architecture

### Database Schema (Supabase)
1. **law_folders** - Main law categories/folders
2. **laws** - Individual law documents
3. **law_articles** - Parsed articles from each law
4. **law_embeddings** - Vector embeddings for semantic search
5. **query_logs** - Query analytics and monitoring

### Edge Functions
1. **query-law** - Main AI query endpoint
2. **generate-embeddings** - Creates vector embeddings for articles
3. **update-laws** - Triggers daily law update checks

### Python Scraper
- **saudi_law_scraper.py** - Web scraper using Scrapling library

## 🚀 Setup Instructions

### Prerequisites

1. **Supabase Account** (Already configured)
   - Database is set up with all tables
   - Edge Functions are deployed
   - Environment variables are configured

2. **OpenAI API Key** (Required)
   - You need to add your OpenAI API key to Supabase secrets
   - Used for generating embeddings and AI responses

### Step 1: Add OpenAI API Key

You need to add your OpenAI API key as a Supabase secret:

```bash
# This will be configured through Supabase Dashboard or CLI
# Secret name: OPENAI_API_KEY
# Get your API key from: https://platform.openai.com/api-keys
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Environment Variables

Create a `.env` file or set these variables:

```bash
export SUPABASE_URL="https://exilgibjcnrtashitzjk.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key_here"
```

### Step 4: Run Initial Scrape

```bash
# Full scrape (first time)
python saudi_law_scraper.py

# This will:
# 1. Scrape all law folders
# 2. Extract all laws from each folder
# 3. Parse articles from each law
# 4. Store everything in Supabase
```

### Step 5: Generate Embeddings

After scraping, generate vector embeddings for semantic search:

```bash
curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/generate-embeddings \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

Or visit the function URL in your browser to trigger it.

### Step 6: Test the System

Open `web/index.html` in your browser or host it on any web server.

Example questions to try:
- ما هي حقوق الموظف عند إنهاء العقد؟
- ماذا ينص نظام العمل عن ساعات العمل؟
- What are the requirements for establishing a company in Saudi Arabia?

## 🔄 Daily Updates

To check for law updates daily:

```bash
# Run update check
python saudi_law_scraper.py update
```

This command:
1. Checks all existing laws in the database
2. Compares publication dates with the website
3. Updates any laws that have changed
4. Re-parses articles for updated laws

You can automate this with a cron job:

```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * cd /path/to/project && python saudi_law_scraper.py update
```

## 🔌 API Usage

### Query Law API

**Endpoint**: `POST /functions/v1/query-law`

**Request**:
```json
{
  "question": "ما هي حقوق الموظف؟",
  "language": "ar",
  "max_results": 5
}
```

**Response**:
```json
{
  "answer": "بناءً على نظام العمل السعودي، للموظف عدة حقوق...",
  "citations": [
    {
      "law_name_ar": "نظام العمل",
      "law_number": "م/51",
      "article_number": "74",
      "article_title_ar": "حقوق العامل عند إنهاء العقد",
      "publication_date": "2005-04-23",
      "law_url": "https://laws.boe.gov.sa/...",
      "similarity": 0.87
    }
  ],
  "response_time_ms": 1250
}
```

### Generate Embeddings API

**Endpoint**: `POST /functions/v1/generate-embeddings`

Processes up to 100 articles at a time. Run multiple times until all articles have embeddings.

### Example cURL Commands

```bash
# Query the AI
curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/query-law \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "ما هي حقوق الموظف؟", "language": "ar"}'

# Generate embeddings
curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/generate-embeddings \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

## 📊 Response Format

Every AI response includes:

1. **اسم النظام** (Law Name) - Full name of the law in Arabic
2. **رقم المادة** (Article Number) - Specific article number
3. **تاريخ النشر** (Publication Date) - When the law was published
4. **رابط النظام** (Law URL) - Direct link to the law on the official website

## 🛠️ Customization

### Adjusting Scraper Selectors

The website structure may change. Update CSS selectors in `saudi_law_scraper.py`:

```python
# Find folders
folder_elements = response.css('a[href*="/BoeLaws/Laws/Folders/"]').getall()

# Find laws
law_elements = response.css('a[href*="/BoeLaws/Laws/"]').getall()

# Find articles
article_elements = response.css('.article, .law-article').getall()
```

### Changing AI Model

In `supabase/functions/query-law/index.ts`, modify the model:

```typescript
model: "gpt-4-turbo-preview", // Change to gpt-4, gpt-3.5-turbo, etc.
```

### Adjusting Search Parameters

Modify similarity threshold and result count:

```typescript
match_threshold: 0.5,  // 0-1, higher = more strict
match_count: 5,        // Number of results
```

## 📁 File Structure

```
project/
├── saudi_law_scraper.py           # Main scraper script
├── requirements.txt                # Python dependencies
├── SAUDI_LAW_AI_README.md         # This file
├── web/
│   └── index.html                 # Web interface
└── supabase/
    └── functions/
        ├── query-law/             # AI query endpoint
        ├── generate-embeddings/   # Embedding generator
        └── update-laws/           # Update checker
```

## 🔍 Troubleshooting

### Issue: No results found

1. Check if laws are scraped: Query `law_folders` and `laws` tables
2. Verify embeddings are generated: Query `law_embeddings` table
3. Check OpenAI API key is configured correctly

### Issue: Scraper returns empty results

1. Website structure may have changed - inspect the HTML
2. Update CSS selectors in the scraper
3. Check if the website is accessible (try manual visit)
4. Verify SSL certificates are valid

### Issue: Slow responses

1. Reduce `max_results` parameter
2. Optimize database indexes
3. Consider caching frequent queries
4. Use faster embedding models

### Issue: Arabic text appears broken

1. Ensure UTF-8 encoding is set everywhere
2. Check database collation settings
3. Verify browser/terminal supports Arabic

## 📈 Performance Tips

1. **Batch Processing**: Generate embeddings in batches to avoid rate limits
2. **Caching**: Cache frequent queries to reduce API calls
3. **Indexing**: Ensure proper indexes on foreign keys and search fields
4. **Rate Limiting**: Add delays between scraper requests
5. **Monitoring**: Use `query_logs` table to track performance

## 🔐 Security Notes

1. Never expose service role key in client-side code
2. Use Row Level Security (RLS) for production
3. Validate and sanitize all user inputs
4. Rate limit API endpoints to prevent abuse
5. Keep OpenAI API key secure

## 📝 License

This project is for educational and research purposes. Always verify legal information with official sources.

## 🤝 Contributing

Feel free to improve the scraper selectors, add more features, or optimize the AI prompts.

## 📞 Support

For issues with:
- **Supabase**: Check Supabase dashboard logs
- **Scraping**: Review website HTML structure
- **AI Responses**: Adjust prompts in query-law function
- **Embeddings**: Check OpenAI API usage and limits

---

Built with ❤️ using Scrapling, Supabase, and OpenAI
