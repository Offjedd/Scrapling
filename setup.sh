#!/bin/bash

# Saudi Law AI Assistant - Setup Script
# This script helps you set up the environment and run the initial scrape

echo "======================================"
echo "Saudi Law AI Assistant - Setup"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ pip3 found"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "======================================"
echo "Environment Setup"
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cat > .env << EOL
SUPABASE_URL=https://exilgibjcnrtashitzjk.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
OPENAI_API_KEY=your_openai_api_key_here
EOL
    echo "📝 Created .env file. Please edit it with your actual keys."
    echo ""
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if environment variables are set
if [ "$SUPABASE_URL" = "your_supabase_url_here" ] || [ "$SUPABASE_SERVICE_ROLE_KEY" = "your_service_role_key_here" ]; then
    echo "⚠️  Please update the .env file with your actual Supabase credentials"
    echo ""
fi

if [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "⚠️  Please update the .env file with your OpenAI API key"
    echo "   Get your key from: https://platform.openai.com/api-keys"
    echo ""
fi

echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next Steps:"
echo ""
echo "1. Edit the .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Run the initial scrape:"
echo "   python3 saudi_law_scraper.py"
echo ""
echo "3. Generate embeddings (after scraping):"
echo "   curl -X POST https://exilgibjcnrtashitzjk.supabase.co/functions/v1/generate-embeddings \\"
echo "     -H \"Authorization: Bearer YOUR_ANON_KEY\""
echo ""
echo "4. Open the web interface:"
echo "   Open web/index.html in your browser"
echo ""
echo "5. Schedule daily updates (optional):"
echo "   Add to crontab: 0 2 * * * cd $(pwd) && python3 saudi_law_scraper.py update"
echo ""
echo "For detailed instructions, see SAUDI_LAW_AI_README.md"
echo ""
