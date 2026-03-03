#!/bin/bash

echo "=========================================="
echo "Saudi Law AI - Quick Start"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with the required environment variables."
    echo "See .env.example for reference."
    exit 1
fi

echo "✅ .env file found"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    exit 1
fi

echo "✅ Python 3 found"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed!"
    exit 1
fi

echo "✅ Node.js found"
echo ""

# Function to display menu
display_menu() {
    echo ""
    echo "=========================================="
    echo "What would you like to do?"
    echo "=========================================="
    echo "1. Validate database (check current status)"
    echo "2. Run enhanced scraper (populate database)"
    echo "3. Start development server (test frontend)"
    echo "4. Build for production"
    echo "5. View scraper statistics"
    echo "6. Exit"
    echo ""
    read -p "Enter your choice (1-6): " choice
}

# Main loop
while true; do
    display_menu

    case $choice in
        1)
            echo ""
            echo "=========================================="
            echo "Running Database Validation..."
            echo "=========================================="
            python3 validate_database.py
            ;;
        2)
            echo ""
            echo "=========================================="
            echo "Starting Enhanced Scraper..."
            echo "=========================================="
            echo "⚠️  This will take 2-4 hours to complete!"
            echo "The scraper will checkpoint progress automatically."
            echo ""
            read -p "Continue? (y/n): " confirm
            if [ "$confirm" = "y" ]; then
                python3 enhanced_law_scraper.py
            else
                echo "Scraper cancelled."
            fi
            ;;
        3)
            echo ""
            echo "=========================================="
            echo "Starting Development Server..."
            echo "=========================================="
            echo "The app will open at http://localhost:5173"
            echo "Press Ctrl+C to stop the server."
            echo ""
            npm run dev
            ;;
        4)
            echo ""
            echo "=========================================="
            echo "Building for Production..."
            echo "=========================================="
            npm run build
            echo ""
            echo "✅ Build complete! Files are in the 'dist' folder."
            ;;
        5)
            echo ""
            echo "=========================================="
            echo "Scraper Statistics"
            echo "=========================================="
            if [ -f scraper_final_stats.json ]; then
                cat scraper_final_stats.json
            else
                echo "No statistics file found. Run the scraper first."
            fi
            ;;
        6)
            echo ""
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please select 1-6."
            ;;
    esac
done
