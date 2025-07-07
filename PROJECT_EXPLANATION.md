# 🏆 Football History - Complete Project Explanation

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [What This Project Does](#-what-this-project-does)
3. [Architecture & Components](#-architecture--components)
4. [Data Flow](#-data-flow)
5. [Technologies Used](#-technologies-used)
6. [Setup & Installation](#-setup--installation)
7. [Usage Guide](#-usage-guide)
8. [Script System](#-script-system)
9. [Web Interface](#-web-interface)
10. [Database Structure](#-database-structure)
11. [Current Capabilities](#-current-capabilities)
12. [Limitations & Future Improvements](#-limitations--future-improvements)

## 🎯 Project Overview

**Football History** is a comprehensive Django web application designed to collect, process, and visualize football (soccer) match data. The project creates a complete pipeline from data extraction to web-based visualization, allowing users to explore football statistics and match information through an intuitive interface.

## 🔍 What This Project Does

### Core Functionality
- **Data Extraction**: Automatically scrapes football match data from FBref.com
- **Logo Collection**: Downloads team and league logos from SofaScore.com
- **Data Processing**: Cleans, normalizes, and standardizes team names and match information
- **Database Storage**: Stores all data in a structured SQLite database
- **Web Visualization**: Provides multiple views for exploring match data by week or league
- **Search Functionality**: Allows searching for specific matches and teams

### Target Use Cases
- Football enthusiasts wanting to analyze match data
- Researchers studying football statistics
- Developers learning about web scraping and data processing
- Anyone interested in football data visualization

## 🏗 Architecture & Components

### 1. **Django Web Application**
- **Framework**: Django 5.1.7
- **Database**: SQLite (development) with support for PostgreSQL (production)
- **Frontend**: Bootstrap 5 with custom CSS
- **Templates**: Responsive HTML templates with multiple view options

### 2. **Script System**
- **Runner Script**: Central orchestrator (`scripts/runner.py`)
- **Export Module**: Data extraction from FBref (`scripts/export_data/`)
- **Import Module**: Database import functionality (`scripts/import_data/`)
- **Logo Scraper**: Automated logo downloading (`scripts/logo_scraper/`)

### 3. **Data Models**
- **Season**: Football seasons (e.g., "2024-2025")
- **League**: Football leagues with country information
- **Team**: Football teams with logos and standardized names
- **Match**: Individual matches with scores, dates, and statistics
- **MatchDay**: Grouping matches by league rounds/gameweeks

## 🔄 Data Flow

```
1. FBref.com → Export Script → CSV Files
2. SofaScore.com → Logo Scraper → PNG Logo Files
3. CSV Files → Import Script → Django Database
4. Database → Django Views → Web Interface
```

### Detailed Process:
1. **Data Extraction**: The export script visits FBref.com, extracts match data for a specific league/season, and saves it to CSV format
2. **Logo Collection**: The logo scraper visits SofaScore.com, identifies teams, and downloads their logos
3. **Data Import**: The import script reads CSV files and populates the Django database with structured data
4. **Web Display**: Django views query the database and render match information in various formats

## 💻 Technologies Used

### Backend
- **Python 3.12+**
- **Django 5.1.7** - Web framework
- **SQLite** - Database (development)
- **Pandas 2.2.3** - Data processing
- **BeautifulSoup4** - HTML parsing (via lxml)
- **Playwright** - Web automation for scraping
- **Loguru** - Advanced logging

### Frontend
- **Bootstrap 5** - CSS framework
- **Font Awesome** - Icons
- **Google Fonts** - Typography (Roboto Condensed, Open Sans)
- **Custom CSS** - Additional styling and animations

### Data Processing
- **NumPy 2.2.4** - Numerical operations
- **python-dateutil** - Date parsing
- **PyYAML** - Configuration files

## 🚀 Setup & Installation

### Prerequisites
- Python 3.12 or higher
- Git
- Internet connection (for data scraping)

### Installation Steps
```bash
# 1. Clone the repository
git clone https://github.com/AinaRazafinjato/football_history.git
cd football_history

# 2. Create virtual environment
python -m venv .env
source .env/bin/activate  # On Windows: .env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Start the development server
python manage.py runserver
```

### Access the Application
- Open your browser to `http://localhost:8000/v1/` or `http://localhost:8000/v2/`

## 📚 Usage Guide

### For End Users

#### Getting Match Data
1. **Export Data from FBref** (optional - if you want fresh data):
   ```bash
   python scripts/runner.py export_data/export_data
   ```

2. **Download Team Logos** (optional - for visual enhancement):
   ```bash
   python scripts/runner.py logo_scraper/logo_scraper
   ```

3. **Import Data to Database** (required):
   ```bash
   python scripts/runner.py import_data/import_data --csv "Premier-League-2024-2025.csv"
   ```

#### Viewing Data
- **V1 View**: Weekly match view at `/v1/`
- **V2 View**: League-based view at `/v2/`
- **Search**: Use the search bar to find specific matches or teams

### For Developers

#### Adding New Scripts
1. Create a Python file in an appropriate subdirectory under `scripts/`
2. The runner will automatically detect it
3. Test with: `python scripts/runner.py your_script/your_script`

#### Customizing Data Sources
- Modify `scripts/export_data/config.yaml` for FBref extraction settings
- Update `scripts/logo_scraper/logo_scraper.py` for different logo sources

## ⚙ Script System

### Runner Script (`scripts/runner.py`)
Central orchestrator that automatically discovers and executes any Python script in the project.

**Usage**:
```bash
# List all available scripts
python scripts/runner.py

# Execute a specific script with arguments
python scripts/runner.py script_name/script_file [arguments]
```

### Available Scripts

#### 1. **export_data/export_data**
- **Purpose**: Extract match data from FBref.com
- **Input**: Web scraping from FBref
- **Output**: CSV files in `data/raw/csv/`
- **Features**: 
  - Configurable via YAML
  - Team name standardization
  - Data cleaning and validation
  - Detailed logging

#### 2. **logo_scraper/logo_scraper**
- **Purpose**: Download team and league logos
- **Input**: Team data from SofaScore.com
- **Output**: PNG files in `static/logos/`
- **Features**:
  - Browser automation with Playwright
  - Automatic name standardization
  - Error handling and retries
  - Support for multiple leagues

#### 3. **import_data/import_data**
- **Purpose**: Import CSV data into Django database
- **Input**: CSV files from export script
- **Output**: Populated Django database
- **Options**: `--csv "filename.csv"`
- **Features**:
  - Automatic league/season detection
  - Team and match creation
  - Data validation
  - Logo association

#### 4. **import_data/constants**
- **Purpose**: Shared constants and mappings
- **Content**: Team name standardization mappings
- **Usage**: Imported by other scripts

### Script Configuration
- **Logging**: All scripts use Loguru for detailed logging
- **Error Handling**: Comprehensive error handling with meaningful messages
- **Modularity**: Each script can be run independently
- **Extensibility**: Easy to add new scripts to the system

## 🌐 Web Interface

### Two View Modes

#### V1 - Weekly View (`/v1/`)
- **Purpose**: Display matches organized by calendar weeks
- **Features**:
  - Pagination by week
  - Automatic navigation to current week
  - Match details with scores and teams
  - Clean, calendar-like layout

#### V2 - League View (`/v2/`)
- **Purpose**: Display matches organized by league and season
- **Features**:
  - League-based filtering
  - Season selection
  - Advanced match statistics
  - Team logo integration

### Common Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Search Functionality**: Find specific matches or teams
- **Professional Styling**: Bootstrap-based with custom enhancements
- **Performance**: Optimized queries and pagination
- **Accessibility**: Semantic HTML and proper navigation

### User Interface Elements
- **Navigation Bar**: Fixed top navigation with search
- **Match Cards**: Clean display of match information
- **Team Logos**: Visual team identification
- **Pagination**: Easy navigation through large datasets
- **Footer**: Additional navigation and branding

## 💾 Database Structure

### Core Models

#### **Season**
- `season_name`: String (e.g., "2024-2025")
- `start_date`: Date of season start
- `end_date`: Date of season end

#### **League**
- `league_name`: String (e.g., "Premier League")
- `country`: String (e.g., "England")
- `logo`: Image field for league logo

#### **Team**
- `team_name`: Full team name
- `short_name`: Abbreviated name (auto-generated)
- `logo`: Image field for team logo
- `league`: Foreign key to League

#### **Match**
- `match_date`: Date of the match
- `time`: Match time (optional)
- `score_home`/`score_away`: Match scores
- `xG_home`/`xG_away`: Expected goals statistics
- `team_home`/`team_away`: Foreign keys to teams
- `day`: Foreign key to MatchDay

#### **Relational Models**
- **LeagueSeason**: Links leagues to seasons
- **TeamSeason**: Links teams to specific league seasons
- **MatchDay**: Groups matches by gameweek/round

### Data Integrity
- **Unique Constraints**: Prevent duplicate matches and teams
- **Validation**: Ensure data consistency (e.g., team can't play itself)
- **Relationships**: Proper foreign key relationships
- **Indexing**: Optimized for common queries

## ✨ Current Capabilities

### What Works Well
1. **Data Pipeline**: Complete end-to-end data flow from web scraping to visualization
2. **Premier League Support**: Full support for English Premier League data
3. **Logo Integration**: Automatic team and league logo downloading and display
4. **Web Interface**: Professional, responsive web interface with multiple views
5. **Search**: Functional search across matches and teams
6. **Data Quality**: Automatic team name standardization and data cleaning
7. **Logging**: Comprehensive logging for debugging and monitoring
8. **Modularity**: Well-structured, modular codebase

### Supported Data Sources
- **FBref.com**: Match data, scores, statistics
- **SofaScore.com**: Team and league logos
- **Manual CSV**: Import from custom CSV files

### Browser Support
- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **Mobile Devices**: Responsive design for tablets and phones

## 🔧 Limitations & Future Improvements

### Current Limitations
1. **League Support**: Currently optimized for Premier League only
2. **Manual Process**: Requires manual script execution for data updates
3. **Real-time Data**: No live match updates (static data only)
4. **Language**: Interface primarily in French
5. **Single Season**: Focus on one season at a time
6. **Bootstrap Dependency**: Requires local Bootstrap files

### Planned Improvements
1. **Multi-League Support**: Extend to other major leagues (La Liga, Serie A, Bundesliga)
2. **Automation**: Scheduled data updates via cron jobs or Celery
3. **Live Data**: Real-time score updates and match tracking
4. **Internationalization**: Multi-language support
5. **Advanced Analytics**: Player statistics, team performance metrics
6. **API**: RESTful API for external data access
7. **User Management**: User accounts and personalized features
8. **Data Visualization**: Charts and graphs for statistical analysis
9. **Mobile App**: Native mobile application
10. **Cloud Deployment**: Production deployment with PostgreSQL

### Technical Debt
- **Error Handling**: Could be more robust in edge cases
- **Testing**: Limited test coverage
- **Documentation**: Code could use more inline documentation
- **Performance**: Database queries could be further optimized
- **Security**: Production security hardening needed

## 🎯 Conclusion

Football History is a well-architected project that demonstrates modern web development practices, data pipeline construction, and web scraping techniques. It provides a solid foundation for football data analysis and can be extended in numerous directions based on specific needs.

The project is particularly valuable for:
- **Learning**: Understanding Django, web scraping, and data processing
- **Research**: Analyzing football statistics and trends
- **Development**: Building upon the existing foundation for custom features

Whether you're a football fan, data analyst, or developer, this project offers a comprehensive solution for working with football match data in a structured, scalable way.