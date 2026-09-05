# 🍕 Pakistan Restaurant Lead Generation Pipeline

An automated system to find and organize contact leads for restaurants across Pakistan using web scraping, data cleaning, and machine learning.

## 🎯 Features

- **Multi-Source Data Collection**: Scrapes from Google Maps, Yellow Pages PK, FoodPanda, and Facebook Pages
- **Smart Data Cleaning**: Automatic deduplication, phone number normalization, and city name standardization
- **ML-Powered Classification**: Uses NLP to automatically classify restaurants by cuisine type
- **Intelligent Lead Scoring**: Assigns potential scores based on online presence, ratings, and data quality
- **Multiple Export Formats**: CSV, Excel (with multiple sheets), and JSON outputs
- **Pakistan-Focused**: Optimized for Pakistani cities and business directories

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd restaurant-lead-pipeline

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment file
cp env_example.txt .env

# Edit .env with your API keys
nano .env
```

**Required API Keys:**
- **Google Maps API Key**: For restaurant data from Google Places API
- **Facebook Access Token**: For Facebook Pages scraping (optional)

### 3. Run the Pipeline

```bash
# Quick test (2 cities, limited data)
python main_pipeline.py --test

# Full pipeline (all cities)
python main_pipeline.py --full

# Custom cities
python main_pipeline.py --cities Karachi,Lahore,Islamabad
```

## 📊 Pipeline Overview

```
Data Collection → Data Cleaning → ML Classification → Lead Scoring → Export
     ↓              ↓              ↓              ↓           ↓
 4 Sources    Deduplication   Cuisine Type   Potential    CSV/Excel/JSON
```

### 1. Data Collection
- **Google Maps**: Restaurant listings with ratings, reviews, and contact info
- **Yellow Pages PK**: Business directory listings
- **FoodPanda**: Food delivery platform restaurant data
- **Facebook Pages**: Business page information

### 2. Data Cleaning
- Remove duplicate restaurants
- Normalize phone numbers to Pakistan format
- Standardize city names
- Clean and validate addresses
- Calculate data quality scores

### 3. ML Classification (Optional)
- **Cuisine Classifier**: Automatically categorizes restaurants by cuisine type
- Uses restaurant names and descriptions
- Supports 17+ cuisine categories
- Fallback to rule-based classification if ML fails

### 4. Lead Scoring (Optional)
- **Lead Scorer**: Assigns 0-100 potential scores
- Considers data completeness, online presence, ratings, city market, etc.
- Categorizes leads as High/Medium/Low/Poor Potential
- Fallback to rule-based scoring if ML fails

### 5. Export
- **CSV**: Simple tabular format
- **Excel**: Multiple sheets with summaries and breakdowns
- **JSON**: Structured data with metadata

## 🏗️ Architecture

```
restaurant-lead-pipeline/
├── data_collectors/          # Web scraping modules
│   ├── google_maps_collector.py
│   ├── yellow_pages_collector.py
│   ├── facebook_collector.py
│   └── foodpanda_collector.py
├── data_cleaning/            # Data processing
│   └── cleaner.py
├── ml_models/               # Machine learning models
│   ├── cuisine_classifier.py
│   └── lead_scorer.py
├── exporters/               # Data export
│   └── data_exporter.py
├── config.py               # Configuration and constants
├── main_pipeline.py        # Main orchestration script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
GOOGLE_MAPS_API_KEY=your_api_key_here

# Optional
FACEBOOK_ACCESS_TOKEN=your_token_here
MAX_RESTAURANTS_PER_CITY=100
DELAY_BETWEEN_REQUESTS=2
TIMEOUT=30
```

### Pakistan Cities Covered

The pipeline automatically covers 20 major Pakistani cities:
- Karachi, Lahore, Islamabad, Rawalpindi, Faisalabad
- Multan, Peshawar, Quetta, Gujranwala, Sialkot
- Bahawalpur, Sargodha, Jhang, Sheikhupura, Rahim Yar Khan
- Gujrat, Kasur, Okara, Mianwali, Sahiwal

### Cuisine Types

Automatically classifies restaurants into 17+ categories:
- Pakistani, BBQ, Chinese, Fast Food, Italian, Thai
- Indian, Turkish, Lebanese, Mexican, Japanese, Korean
- American, European, Fusion, Desserts, Beverages

## 📈 Output Format

### Excel Export Structure

1. **All Restaurants**: Complete dataset with all fields
2. **Summary**: Key statistics and metrics
3. **City Breakdown**: Restaurant counts and metrics by city
4. **Cuisine Breakdown**: Restaurant counts and metrics by cuisine
5. **High Potential Leads**: Top-scoring restaurants for outreach
6. **Data Quality**: Completeness analysis by field and source

### Key Fields

- **Basic Info**: Name, City, Cuisine Type, Address
- **Contact**: Phone, Website, Social Media
- **Metrics**: Rating, Reviews Count, Quality Score
- **ML Outputs**: Predicted Cuisine, Lead Score, Lead Potential
- **Metadata**: Source, Collection Date, Data Quality

## 🤖 Machine Learning Features

### Cuisine Classification
- **Model**: TF-IDF + Naive Bayes/Random Forest
- **Features**: Restaurant names, descriptions, keywords
- **Accuracy**: Typically 80-90% with sufficient training data
- **Fallback**: Rule-based classification using keyword matching

### Lead Scoring
- **Model**: Random Forest/Gradient Boosting/Linear Regression
- **Features**: 10+ engineered features (completeness, presence, ratings, etc.)
- **Output**: 0-100 potential score with confidence
- **Fallback**: Rule-based scoring using weighted feature averages

## 🚨 Important Notes

### Rate Limiting
- Built-in delays between requests to respect website policies
- Configurable timeouts and retry mechanisms
- Respects robots.txt and ethical scraping practices

### API Limits
- Google Maps: 1000 requests/day (free tier)
- Facebook: Rate limited, requires access token
- Yellow Pages/FoodPanda: Web scraping with delays

### Legal Considerations
- Only scrape publicly available information
- Respect website terms of service
- Use for legitimate business purposes only
- Consider obtaining permission for commercial use

## 🔍 Troubleshooting

### Common Issues

1. **No data collected**: Check API keys and internet connection
2. **ML training fails**: Ensure sufficient data (minimum 10 samples)
3. **Export errors**: Check write permissions for output directory
4. **Rate limiting**: Increase delays between requests

### Debug Mode

```python
# In main_pipeline.py, add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Usage Examples

### Basic Usage

```python
from main_pipeline import RestaurantLeadPipeline

# Initialize pipeline
pipeline = RestaurantLeadPipeline()

# Run quick test
df = pipeline.run_quick_test()

# Run full pipeline
df = pipeline.run_full_pipeline()

# Custom cities
df = pipeline.run_full_pipeline(['Karachi', 'Lahore'])
```

### Individual Components

```python
# Data collection only
restaurants = pipeline.collect_data(['Karachi'], max_per_city=50)

# Data cleaning only
cleaned_df = pipeline.clean_data()

# ML classification only
classified_df = pipeline.classify_cuisines(cleaned_df)

# Lead scoring only
scored_df = pipeline.score_leads(classified_df)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational and legitimate business purposes. Please respect website terms of service and applicable laws.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review error logs
3. Open an issue on GitHub
4. Ensure you have valid API keys

## 🔮 Future Enhancements

- **Additional Sources**: Zomato, TripAdvisor, Instagram
- **Advanced ML**: Deep learning for cuisine classification
- **Real-time Updates**: Continuous data collection
- **API Endpoints**: REST API for integration
- **Dashboard**: Web interface for monitoring and analysis
- **Automation**: Scheduled runs and email reports

---

**Happy Lead Generation! 🎯** 

## 🚀 Professional GitHub Setup Guide

### 1. **Create a Professional .gitignore File**

First, create a `.gitignore` file to exclude unnecessary files:

```gitignore
<code_block_to_apply_changes_from>
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# Environment variables
.env
.env.local
.env.*.local

# Logs
*.log
logs/
pipeline.log

# Output files
output/
web_output/
test_output/
temp/
*.csv
*.xlsx
*.json

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
```

### 2. **Initialize Git Repository**

Open your terminal in the project directory and run:

```bash
# Initialize git repository
git init

# Add all files (excluding .gitignore patterns)
git add .

# Make initial commit
git commit -m "Initial commit: Pakistan Restaurant Lead Generation Pipeline

- Multi-source data collection from Google Maps, Yellow Pages, FoodPanda, Facebook
- Smart data cleaning and deduplication
- ML-powered cuisine classification and lead scoring
- Multiple export formats (CSV, Excel, JSON)
- Pakistan-focused restaurant lead generation system"
```

### 3. **Create GitHub Repository**

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Repository name: `pakistan-restaurant-lead-pipeline` (or your preferred name)
4. Description: `🍕 Automated restaurant lead generation pipeline for Pakistan using web scraping, ML, and data analysis`
5. Make it **Public** (for open source)
6. **Don't** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### 4. **Link and Push to GitHub**

```bash
# Add remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/pakistan-restaurant-lead-pipeline.git

# Set main branch (GitHub standard)
git branch -M main

# Push to GitHub
git push -u origin main
```

### 5. **Professional Repository Setup**

After pushing, enhance your repository:

#### **Add Repository Topics** (on GitHub):
- `restaurant-leads`
- `pakistan`
- `web-scraping`
- `machine-learning`
- `data-pipeline`
- `lead-generation`
- `python`

#### **Update README.md** (if needed):
Your README is already excellent! Just ensure the clone URL is correct:

```markdown
# Clone the repository
git clone https://github.com/YOUR_USERNAME/pakistan-restaurant-lead-pipeline.git
```

### 6. **Additional Professional Touches**

#### **Create LICENSE file** (MIT License recommended for open source):

```text
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

#### **Add CONTRIBUTING.md** (optional but professional):

```markdown
# Contributing to Pakistan Restaurant Lead Generation Pipeline

We love your input! We want to make contributing to this project as easy and transparent as possible.

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

1. Clone your fork
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `env_example.txt` to `.env` and configure
4. Run tests: `python -m pytest`

## Code Style

- Follow PEP 8 guidelines
- Add docstrings to functions
- Include type hints where possible
- Write tests for new features
```

### 7. **Final Commands**

```bash
# Add new files
git add LICENSE CONTRIBUTING.md

# Commit
git commit -m "Add MIT License and Contributing guidelines"

# Push
git push origin main
```

### 8. **GitHub Features to Enable**

- **Issues**: Enable for bug reports and feature requests
- **Discussions**: Enable for community engagement
- **Actions**: Enable for CI/CD (optional)
- **Wiki**: Enable for detailed documentation

### 9. **Professional Maintenance**

- Keep dependencies updated
- Respond to issues and pull requests promptly
- Regular releases with semantic versioning
- Update documentation as features evolve

Your project is already very well-structured and professional! The README is comprehensive, the code is organized, and you have proper testing. This will make an excellent open-source contribution to the community.

Would you like me to help you with any specific part of this process, or do you have questions about any of these steps? 