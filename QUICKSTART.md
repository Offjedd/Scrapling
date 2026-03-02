# Quick Start Guide - Saudi Law AI Assistant

## ✅ System Status

All components are implemented and deployed:

- ✅ Database schema created (5 tables with RLS)
- ✅ Web scraper built (using Scrapling)
- ✅ Edge Functions deployed (3 functions)
- ✅ Web interface ready
- ✅ Testing tools available
- ✅ Documentation complete (English + Arabic)

## 🚀 Get Started in 5 Steps

### Step 1: Add Your OpenAI API Key ⚡

You need an OpenAI API key to generate embeddings and AI responses.

1. Go to https://platform.openai.com/api-keys
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy your key

**Note**: You'll need to add this as a Supabase secret. The system will guide you.

### Step 2: Install Dependencies 📦

```bash
# Run the automated setup
bash setup.sh

# Or manually
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables 🔧

Edit the `.env` file (or set environment variables):

```bash
export SUPABASE_URL="https://exilgibjcnrtashitzjk.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="<get_from_supabase_dashboard>"
export OPENAI_API_KEY="<your_openai_key>"
```

### Step 4: Run Initial Scrape 🕷️

```bash
# This will scrape all laws from the website
# It may take some time depending on the website
python saudi_law_scraper.py
```

The scraper will:
- ✅ Find all law folders
- ✅ Extract all laws from each folder
- ✅ Parse articles from each law
- ✅ Save everything to the database

### Step 5: Generate Embeddings 🧠

After scraping, generate vector embeddings:

```bash
# Method 1: Using curl
curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/generate-embeddings \
  -H "Authorization: Bearer <YOUR_ANON_KEY>"

# Method 2: Open in browser
# Visit: https://exilgibjcnrtashitzjk.supabase.co/functions/v1/generate-embeddings
```

**Note**: This processes 100 articles at a time. Run multiple times until all articles have embeddings.

## 🎉 You're Ready!

### Test the System

#### Option 1: Web Interface
Open `web/index.html` in your browser and start asking questions!

Example questions:
- ما هي حقوق الموظف عند إنهاء العقد؟
- ماذا ينص نظام العمل عن ساعات العمل؟
- What are the requirements for establishing a company?

#### Option 2: Command Line Testing
```bash
# Run sample tests
python test_query.py

# Interactive mode
python test_query.py --interactive

# Test specific question
python test_query.py "ما هي حقوق الموظف؟"
```

#### Option 3: Direct API Call
```bash
curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/query-law \
  -H "Authorization: Bearer <YOUR_ANON_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "ما هي حقوق الموظف؟",
    "language": "ar",
    "max_results": 5
  }'
```

## 🔄 Daily Updates

To keep the laws up-to-date, run the update checker:

```bash
# Manual update
python saudi_law_scraper.py update

# Or via Edge Function
curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/update-laws
```

### Automate Daily Updates (Optional)

Add to crontab to run daily at 2 AM:

```bash
crontab -e

# Add this line:
0 2 * * * cd /path/to/project && python saudi_law_scraper.py update
```

## 📊 Expected Response Format

Every answer includes:

```json
{
  "answer": "بناءً على نظام العمل السعودي...",
  "citations": [
    {
      "law_name_ar": "نظام العمل",
      "law_number": "م/51",
      "article_number": "74",
      "article_title_ar": "حقوق العامل",
      "publication_date": "2005-04-23",
      "law_url": "https://laws.boe.gov.sa/...",
      "similarity": 0.87
    }
  ],
  "response_time_ms": 1250
}
```

## 🛠️ Troubleshooting

### Problem: Scraper finds no data
**Solution**: The website structure may have changed. Check the HTML and update CSS selectors in `saudi_law_scraper.py`

### Problem: No embeddings generated
**Solution**:
1. Check if OpenAI API key is configured
2. Verify you have articles in the database
3. Check OpenAI API usage limits

### Problem: AI returns no results
**Solution**:
1. Ensure embeddings are generated
2. Check if laws are in the database
3. Try lowering the similarity threshold

### Problem: Arabic text looks broken
**Solution**:
1. Ensure UTF-8 encoding everywhere
2. Check browser language support
3. Verify database collation

## 📚 Documentation

For detailed information, see:

- **SAUDI_LAW_AI_README.md** - Complete English documentation
- **دليل_الاستخدام.md** - Full Arabic guide
- **PROJECT_SUMMARY.md** - Technical overview

## 🔐 Important Security Notes

1. **Never expose** your `SUPABASE_SERVICE_ROLE_KEY` in client-side code
2. Use `SUPABASE_ANON_KEY` for web interface
3. Keep your OpenAI API key secure
4. Monitor API usage to avoid unexpected costs

## 💡 Tips for Best Results

1. **Scraping**: Run full scrape during off-peak hours
2. **Embeddings**: Generate in batches to avoid rate limits
3. **Queries**: Arabic questions typically get better results
4. **Updates**: Check for law updates weekly or daily
5. **Monitoring**: Review query logs for popular questions

## 🎯 What's Included

```
✅ Database: 5 tables with vector search
✅ Scraper: Full website extraction with Arabic support
✅ AI Query: GPT-4 with complete citations
✅ Embeddings: Semantic search with OpenAI
✅ Web UI: Beautiful bilingual interface
✅ Testing: Automated test scripts
✅ Docs: Complete in English + Arabic
✅ Updates: Daily law change detection
```

## 📞 Need Help?

1. Check the main documentation files
2. Review inline code comments
3. Test with sample questions first
4. Monitor Supabase dashboard for errors
5. Check OpenAI usage dashboard

## 🎓 Legal Disclaimer

This system is for informational and educational purposes only. It does not constitute legal advice. Always verify information with official sources and consult qualified legal professionals for legal matters.

---

**Ready to go!** Open `web/index.html` or run `python test_query.py` to start! 🚀

For detailed setup and customization, see the full documentation.
