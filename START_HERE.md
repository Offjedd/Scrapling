# 🏛️ Saudi Arabian Law AI Assistant
## مساعد الأنظمة السعودية الذكي

> **Status**: ✅ COMPLETE - Ready for use!

An intelligent AI system that answers questions about Saudi Arabian laws with complete citations including law name, article number, publication date, and URL.

---

## 🎯 What This System Does

Ask any question about Saudi law in Arabic or English, and get accurate answers with complete legal citations:

**Question**: "ما هي حقوق الموظف عند إنهاء العقد؟"

**Answer**: Detailed explanation with:
- ✅ Law name (اسم النظام)
- ✅ Article number (رقم المادة)
- ✅ Publication date (تاريخ النشر)
- ✅ Direct link (رابط النظام)

---

## 🚀 Quick Start (3 Minutes)

### 1. Install Dependencies
```bash
bash setup.sh
```

### 2. Add OpenAI API Key
Get your key from https://platform.openai.com/api-keys and add to `.env`:
```
OPENAI_API_KEY=your_key_here
```

### 3. Scrape Laws & Generate Embeddings
```bash
# Scrape all laws from the website
python saudi_law_scraper.py

# Generate embeddings for AI search
curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/generate-embeddings \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

### 4. Start Using!
```bash
# Option A: Web interface
open web/index.html

# Option B: Command line
python test_query.py --interactive

# Option C: Direct API
curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/query-law \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"question": "ما هي حقوق الموظف؟", "language": "ar"}'
```

---

## 📚 Documentation

Choose your preferred guide:

### For Quick Setup:
- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 steps

### For Detailed Information:
- **[SAUDI_LAW_AI_README.md](SAUDI_LAW_AI_README.md)** - Complete English documentation
- **[دليل_الاستخدام.md](دليل_الاستخدام.md)** - Full Arabic guide

### For Technical Details:
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Architecture and implementation
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Completion checklist

---

## ✨ Key Features

- 🤖 **AI-Powered**: Uses GPT-4 optimized for Arabic legal terminology
- 🔍 **Semantic Search**: Understands meaning, not just keywords
- 📖 **Complete Citations**: Every answer includes law name, article, date, and URL
- 🌐 **Bilingual**: Works in both Arabic and English
- 🔄 **Auto-Update**: Daily checks for law changes
- 💻 **Web Interface**: Beautiful, responsive UI
- 🔒 **Secure**: Row-level security and API key protection

---

## 🏗️ What's Included

### ✅ Components Deployed:
- Database with 5 tables (vector search enabled)
- 3 Edge Functions (query, embeddings, updates)
- Web scraper using Scrapling library
- Web interface with bilingual support
- Testing tools (interactive + automated)
- Complete documentation (English + Arabic)

### 📦 Files:
```
project/
├── START_HERE.md                  ← You are here
├── QUICKSTART.md                  ← Quick setup guide
├── SAUDI_LAW_AI_README.md        ← Detailed English docs
├── دليل_الاستخدام.md              ← Arabic guide
├── PROJECT_SUMMARY.md             ← Technical overview
├── IMPLEMENTATION_COMPLETE.md     ← Completion status
│
├── saudi_law_scraper.py           ← Web scraper
├── test_query.py                  ← Testing tool
├── setup.sh                       ← Setup automation
├── requirements.txt               ← Dependencies
├── .env.example                   ← Config template
│
├── web/
│   └── index.html                ← Web interface
│
└── supabase/functions/
    ├── query-law/                ← AI query endpoint
    ├── generate-embeddings/      ← Embedding generator
    └── update-laws/              ← Update checker
```

---

## 🎯 System Architecture

```
User Question
     ↓
Web Interface (web/index.html)
     ↓
Edge Function: query-law
     ↓
Database: Vector Search + Full-Text
     ↓
AI Response with Citations
     ↓
Display: Law Name, Article, Date, URL
```

**Data Source**: https://laws.boe.gov.sa/BoeLaws/Laws/Folders/

---

## 💡 Example Questions

Try these in the web interface or command line:

### Arabic Questions:
- ما هي حقوق الموظف عند إنهاء العقد؟
- ماذا ينص نظام العمل عن ساعات العمل الإضافية؟
- ما هي شروط تأسيس شركة في السعودية؟
- كيف يتم احتساب إجازة الموظف السنوية؟
- ما هي حقوق المستهلك في التجارة الإلكترونية؟

### English Questions:
- What are the employee rights upon contract termination?
- What are the requirements for establishing a company in Saudi Arabia?
- What does the labor law say about working hours?

---

## 🔄 Daily Updates

Keep laws up-to-date by running the update checker:

```bash
# Manual update
python saudi_law_scraper.py update

# Or schedule with cron (daily at 2 AM)
0 2 * * * cd /path/to/project && python saudi_law_scraper.py update
```

---

## 🛠️ Technology Stack

- **Database**: Supabase (PostgreSQL + pgvector)
- **Scraping**: Scrapling library (Python)
- **AI**: OpenAI GPT-4 + text-embedding-3-small
- **Frontend**: HTML/CSS/JavaScript
- **Backend**: Supabase Edge Functions (Deno)

---

## 📊 Response Format

Every answer includes these required elements:

```json
{
  "answer": "بناءً على نظام العمل السعودي، المادة 74...",
  "citations": [
    {
      "law_name_ar": "نظام العمل",           // اسم النظام
      "law_number": "م/51",
      "article_number": "74",                  // رقم المادة
      "publication_date": "2005-04-23",        // تاريخ النشر
      "law_url": "https://laws.boe.gov.sa/..." // رابط النظام
    }
  ]
}
```

---

## 🔐 Security & Privacy

- ✅ Row Level Security (RLS) enabled
- ✅ API keys protected
- ✅ Input validation
- ✅ CORS properly configured
- ✅ No user data stored (except query logs for analytics)

---

## 📞 Need Help?

1. **Quick Setup**: Read [QUICKSTART.md](QUICKSTART.md)
2. **Detailed Guide**: Read [SAUDI_LAW_AI_README.md](SAUDI_LAW_AI_README.md)
3. **Arabic Guide**: Read [دليل_الاستخدام.md](دليل_الاستخدام.md)
4. **Technical Info**: Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
5. **Check Status**: Read [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

---

## ⚖️ Legal Disclaimer

This system is for informational and educational purposes only. It does not constitute legal advice. Always verify information with official sources and consult qualified legal professionals for legal matters.

---

## 📈 Project Stats

- **Lines of Code**: ~2,500+
- **Database Tables**: 5
- **Edge Functions**: 3 (all ACTIVE)
- **Documentation**: 5 comprehensive guides
- **Languages**: Arabic (primary), English (secondary)
- **Status**: ✅ Production Ready

---

## 🎉 Ready to Use!

The system is complete and ready. Just follow the Quick Start section above!

**Next Steps**:
1. Run `bash setup.sh`
2. Add OpenAI API key
3. Run scraper
4. Generate embeddings
5. Start asking questions!

---

**Built with ❤️ using Scrapling, Supabase, and OpenAI**

For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md)
