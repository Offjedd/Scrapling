#!/bin/bash

# Saudi Law AI - Complete Initial Setup
# This script runs everything needed to get the system working

echo "======================================================"
echo "Saudi Law AI Assistant - Initial Setup"
echo "======================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found: $(python3 --version)${NC}"
echo ""

# Step 2: Install dependencies
echo "Step 2: Installing Python dependencies..."
pip3 install -r requirements.txt -q
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Step 3: Check environment variables
echo "Step 3: Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Creating .env from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env with your API keys${NC}"
    exit 1
fi
echo -e "${GREEN}✅ .env file found${NC}"
echo ""

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Step 4: Test OpenAI connection
echo "Step 4: Testing OpenAI API connection..."
python3 test_openai_connection.py
echo ""

# Step 5: Run the scraper
echo "======================================================"
echo "Step 5: Starting Law Scraper"
echo "======================================================"
echo ""
echo -e "${YELLOW}This will scrape laws from the Saudi government website.${NC}"
echo -e "${YELLOW}It may take some time (minutes to hours) depending on the number of laws.${NC}"
echo ""
read -p "Do you want to start scraping now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting scraper..."
    python3 saudi_law_scraper.py

    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ Scraping completed successfully!${NC}"
    else
        echo ""
        echo -e "${RED}❌ Scraping failed. Please check the error messages above.${NC}"
        exit 1
    fi
else
    echo ""
    echo -e "${YELLOW}Skipped scraping. You can run it manually later:${NC}"
    echo "  python3 saudi_law_scraper.py"
    exit 0
fi

# Step 6: Generate embeddings
echo ""
echo "======================================================"
echo "Step 6: Generating Vector Embeddings"
echo "======================================================"
echo ""
echo -e "${YELLOW}This will create AI embeddings for semantic search.${NC}"
echo -e "${YELLOW}It processes 100 articles at a time and may take several minutes.${NC}"
echo ""
read -p "Do you want to generate embeddings now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Generating embeddings..."

    # Get anon key from .env
    ANON_KEY=$(grep VITE_SUPABASE_ANON_KEY .env | cut -d '=' -f2)

    curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/generate-embeddings \
      -H "Authorization: Bearer $ANON_KEY" \
      -H "Content-Type: application/json"

    echo ""
    echo ""
    echo -e "${GREEN}✅ First batch of embeddings generated!${NC}"
    echo -e "${YELLOW}Note: You may need to run this multiple times to process all articles.${NC}"
    echo ""
    echo "To process more articles, run:"
    echo "  curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/generate-embeddings \\"
    echo "    -H \"Authorization: Bearer $ANON_KEY\""
else
    echo ""
    echo -e "${YELLOW}Skipped embedding generation. You can run it manually later.${NC}"
fi

# Step 7: Final instructions
echo ""
echo "======================================================"
echo "🎉 Setup Complete!"
echo "======================================================"
echo ""
echo "Your Saudi Law AI Assistant is ready to use!"
echo ""
echo "Next Steps:"
echo ""
echo "1. Test with command line:"
echo "   python3 test_query.py --interactive"
echo ""
echo "2. Open the web interface:"
echo "   open web/index.html"
echo "   (or just open the file in your browser)"
echo ""
echo "3. Try these example questions:"
echo "   - ما هي حقوق الموظف عند إنهاء العقد؟"
echo "   - ماذا ينص نظام العمل عن ساعات العمل؟"
echo "   - What are the requirements for establishing a company?"
echo ""
echo "4. Schedule daily updates (optional):"
echo "   crontab -e"
echo "   # Add this line:"
echo "   0 2 * * * cd $(pwd) && python3 saudi_law_scraper.py update"
echo ""
echo "For more information, see:"
echo "  - QUICKSTART.md"
echo "  - SAUDI_LAW_AI_README.md"
echo "  - دليل_الاستخدام.md"
echo ""
echo "======================================================"
