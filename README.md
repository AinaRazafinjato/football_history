# 🏆 Football History - Football Data Management System

A comprehensive Django web application for extracting, processing, and visualizing football match data from various sources.

## 📖 Documentation
- **🚀 [Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **📋 [Complete Project Explanation](PROJECT_EXPLANATION.md)** - Comprehensive overview of what this project does, how it works, and how to use it effectively

## 🚀 Quick Start

This project allows you to extract football match data from **FBref**, download team logos from **SofaScore**, and visualize everything in a modern Django web application.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AinaRazafinjato/football_history.git
cd football_history

# 2. Create and activate virtual environment
python -m venv .env
source .env/bin/activate  # On Windows: .env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up database
python manage.py migrate

# 5. Start the application
python manage.py runserver
```

### Access the Application
Open your browser to:
- **Weekly view**: http://localhost:8000/v1/
- **League view**: http://localhost:8000/v2/

## 🎯 What This Project Does

### Core Features
- **🔍 Data Extraction**: Scrapes match data from FBref.com
- **🖼️ Logo Collection**: Downloads team logos from SofaScore.com  
- **📊 Data Processing**: Cleans and standardizes team names and match data
- **🌐 Web Interface**: Modern, responsive Django application
- **🔎 Search**: Find specific matches and teams quickly
- **📱 Mobile-Friendly**: Works perfectly on all devices

### Use Cases
- Analyze football statistics and trends
- Research historical match data
- Learn web scraping and Django development
- Explore football data visualization techniques

## 🎮 Quick Usage Guide

The project includes a powerful script runner that automates the entire data pipeline:

### List Available Scripts
```bash
python scripts/runner.py
```

### Complete Data Pipeline
```bash
# 1. Export match data from FBref (optional - creates fresh CSV)
python scripts/runner.py export_data/export_data

# 2. Download team logos from SofaScore (optional - for visual enhancement)  
python scripts/runner.py logo_scraper/logo_scraper

# 3. Import data into Django database (required)
python scripts/runner.py import_data/import_data --csv "Premier-League-2024-2025.csv"
```

### Start the Web Application
```bash
python manage.py runserver
```

Then visit http://localhost:8000/v1/ or http://localhost:8000/v2/ to explore your data!

## 📄 Available Scripts

### 📥 import_data/import_data
**Purpose**: Import match data from CSV files into the Django database

**Features**:
- Automatic league and season detection
- Team creation and standardization  
- Match data validation and import
- Logo association

**Usage**:
```bash
python scripts/runner.py import_data/import_data --csv "Premier-League-2024-2025.csv"
```

### 📤 export_data/export_data  
**Purpose**: Extract match data from FBref.com and save to CSV

**Features**:
- Web scraping from FBref
- Data cleaning and normalization
- Team name standardization
- Configurable via YAML

**Usage**:
```bash
python scripts/runner.py export_data/export_data
```

### 🖼️ logo_scraper/logo_scraper
**Purpose**: Download team and league logos from SofaScore.com

**Features**:
- Automated web browsing with Playwright
- Team logo extraction and download
- Standardized file naming
- Error handling and retries

**Usage**:
```bash
python scripts/runner.py logo_scraper/logo_scraper
```

## 🌟 Key Technologies

- **Backend**: Django 5.1.7, Python 3.12+, SQLite/PostgreSQL
- **Frontend**: Bootstrap 5, Font Awesome, Custom CSS
- **Data Processing**: Pandas, NumPy, BeautifulSoup4
- **Web Scraping**: Playwright, Requests
- **Logging**: Loguru for detailed operation logs

## 📊 Screenshot

Here's what the application looks like:

![Football History Application](https://github.com/user-attachments/assets/312144f9-f104-4c51-bd7a-3d682fd16a99)

*The web interface showing the main navigation and league selection area*

## 🔄 Typical Workflow

```bash
# Complete setup and data pipeline
git clone https://github.com/AinaRazafinjato/football_history.git
cd football_history
python -m venv .env && source .env/bin/activate
pip install -r requirements.txt
python manage.py migrate

# Get fresh data (optional)
python scripts/runner.py export_data/export_data

# Download logos (optional) 
python scripts/runner.py logo_scraper/logo_scraper

# Import data (required)
python scripts/runner.py import_data/import_data --csv "Premier-League-2024-2025.csv"

# Start the application
python manage.py runserver
```

## 📈 Current Status & Capabilities

### ✅ What Works
- Complete data pipeline from web scraping to visualization
- Professional Django web interface with two view modes
- Automated team logo downloading and integration  
- Team name standardization and data cleaning
- Search functionality across matches and teams
- Responsive design for all devices
- Comprehensive logging and error handling

### 🔧 Future Improvements
- Support for multiple leagues (currently optimized for Premier League)
- Real-time match data updates
- Advanced analytics and statistical visualizations
- REST API for external data access
- Multi-language interface support
- User accounts and personalized features

## 📁 Project Structure

```
football_history/
├── football_history/          # Django project configuration  
├── matches/                   # Main Django app for match data
├── scripts/                   # Data pipeline scripts
│   ├── runner.py             # Script orchestrator
│   ├── export_data/          # FBref data extraction
│   ├── import_data/          # Database import functionality  
│   └── logo_scraper/         # SofaScore logo downloading
├── templates/                # HTML templates
├── static/                   # CSS, JS, images, logos
├── data/raw/csv/            # CSV data storage
└── requirements.txt         # Python dependencies
```

## 💡 For Developers

### Adding New Features
- **New Scripts**: Add Python files under `scripts/` - they'll be auto-detected
- **Data Sources**: Extend the export/import scripts for new websites
- **UI Components**: Modify templates and CSS for interface changes
- **Database Models**: Add new models in `matches/models.py`

### Configuration
- **Database**: Settings in `football_history/settings.py`
- **Scripts**: YAML configuration in `scripts/export_data/config.yaml`
- **Styling**: Custom CSS in `static/css/custom.css`

## 🤝 Contributing

This project welcomes contributions! Whether you want to:
- Add support for new leagues
- Improve the user interface
- Enhance data processing capabilities
- Add new visualization features
- Fix bugs or improve performance

Feel free to submit issues and pull requests.

## 📜 License

This project is open source. Please check the repository for license details.

---

**Need more details?** 📖 [Read the complete project explanation](PROJECT_EXPLANATION.md) for in-depth information about architecture, usage, and capabilities.
