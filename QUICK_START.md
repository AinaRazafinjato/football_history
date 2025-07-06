# 🚀 Football History - Quick Start Guide

This guide will get you up and running with Football History in under 5 minutes!

## 🎯 What You'll Achieve
By following this guide, you'll have a working football data visualization website with:
- Match data from FBref.com
- Team logos from SofaScore.com  
- A professional web interface to explore the data

## ⚡ 5-Minute Setup

### Step 1: Get the Code
```bash
git clone https://github.com/AinaRazafinjato/football_history.git
cd football_history
```

### Step 2: Setup Environment  
```bash
# Create virtual environment
python -m venv .env

# Activate it
source .env/bin/activate  # On Windows: .env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Setup Database
```bash
python manage.py migrate
```

### Step 4: Get Data (Optional - Use Sample Data)
If you want to start with fresh data from the web:
```bash
# Get match data from FBref
python scripts/runner.py export_data/export_data

# Download team logos from SofaScore  
python scripts/runner.py logo_scraper/logo_scraper

# Import into database
python scripts/runner.py import_data/import_data --csv "Premier-League-2024-2025.csv"
```

**Note**: The logo scraper uses Playwright which opens a browser - this is normal!

### Step 5: Start the Application
```bash
python manage.py runserver
```

### Step 6: Explore! 
Open your browser to:
- **Weekly View**: http://localhost:8000/v1/
- **League View**: http://localhost:8000/v2/

## 🎮 Using the Interface

### Navigation
- **Search Bar**: Find specific teams or matches
- **Pagination**: Navigate through weeks (v1) or matches (v2)
- **Responsive**: Works on mobile, tablet, and desktop

### Two View Modes
1. **V1 (Weekly)**: Shows matches organized by calendar weeks
2. **V2 (League)**: Shows matches organized by league and season

## 🔧 Troubleshooting

### "No league selected" or Empty Data?
This means you need to import some data first:
```bash
python scripts/runner.py import_data/import_data --csv "Premier-League-2024-2025.csv"
```

### Browser Opens During Logo Scraping?
This is normal! The logo scraper uses Playwright to automate a browser for downloading logos.

### Script Errors?
Check that you're in the right directory and your virtual environment is activated:
```bash
# Make sure you're in the project root
pwd  # Should show .../football_history

# Make sure virtual environment is active  
which python  # Should show path with .env
```

## 📊 Next Steps

### Explore the Data
- Try searching for specific teams like "Arsenal" or "Liverpool"
- Navigate through different weeks to see match schedules
- Check out team logos and match details

### Add More Data
- The scripts work with any FBref league data
- You can import multiple CSV files for different seasons
- Logo scraper can download logos for any league on SofaScore

### Customize
- Modify `static/css/custom.css` for different styling
- Update `templates/` for interface changes
- Add new scripts in `scripts/` for additional data sources

## 📖 Learn More

- **Complete Documentation**: [PROJECT_EXPLANATION.md](PROJECT_EXPLANATION.md)
- **Script System**: `python scripts/runner.py` to see all available scripts
- **Django Admin**: Create superuser with `python manage.py createsuperuser`

## 🆘 Need Help?

1. **Check the logs**: Scripts create detailed logs in `logs/` directory
2. **Read the full documentation**: [PROJECT_EXPLANATION.md](PROJECT_EXPLANATION.md)  
3. **Check script options**: Most scripts have `--help` options
4. **Examine the code**: The codebase is well-commented and modular

Happy exploring! 🏆⚽