# 🤖 AI Lab Jobs Tracker

Automated job posting tracker for major AI labs and companies. Scrapes job boards from OpenAI, Anthropic, DeepMind, Cohere, Hugging Face, Scale AI, Midjourney, Stability AI, and more.

## 🚀 Features

- **Multi-platform scraping**: Supports Greenhouse, Lever, Workday, and Ashby job boards
- **Automated execution**: Runs daily via GitHub Actions
- **Change tracking**: Detects new, updated, and closed job postings
- **Rich metadata**: Captures job details, locations, teams, and descriptions
- **CSV outputs**: Daily snapshots, events log, and current registry

## 📊 Current Coverage

- **OpenAI** (Greenhouse) - Research, Engineering roles
- **Anthropic** (Lever) - AI Safety, Research positions  
- **DeepMind** (Greenhouse) - AI Research, ML Engineering
- **Cohere** (Lever) - NLP, Backend Engineering
- **Hugging Face** (Workday) - Open Source AI, ML
- **Scale AI** (Greenhouse) - Data Labeling, ML Infrastructure
- **Midjourney** (Ashby) - AI Art, Creative Technology
- **Stability AI** (Workday) - AI Image Generation
- **Inflection AI** (Greenhouse) - AI Chat, Personal AI
- **Runway ML** (Greenhouse) - AI Video, Creative Tools
- **Perplexity AI** (Greenhouse) - AI Search, Research

## 🛠️ Setup

### Prerequisites

- Python 3.9+
- Git repository access

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd AIJobs
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run locally**
   ```bash
   # Run for today
   python run_scraper.py
   
   # Run for specific date
   python run_scraper.py --date 2025-08-24
   
   # Verbose mode
   python run_scraper.py --verbose
   ```

## 🤖 Automation

### GitHub Actions (Recommended)

The scraper runs automatically via GitHub Actions:

- **Schedule**: Daily at 9 AM UTC (5 AM EST, 2 AM PST)
- **Manual trigger**: Available from GitHub Actions tab
- **Auto-commit**: Results automatically committed to repository
- **Free tier**: 2,000 minutes/month included

#### Setup Steps

1. **Push the workflow file** (already created: `.github/workflows/scrape-jobs.yml`)
2. **Enable Actions** in your GitHub repository settings
3. **Verify permissions** - Actions need write access to commit results

#### Manual Trigger

1. Go to **Actions** tab in your repository
2. Select **AI Jobs Scraper** workflow
3. Click **Run workflow**
4. Optionally specify a custom date
5. Click **Run workflow**

### Alternative Hosting Options

If you prefer not to use GitHub Actions:

#### Railway (Simple)
- Free tier available
- Easy deployment from GitHub
- Automatic restarts

#### Render (Simple)
- Free tier available  
- GitHub integration
- Scheduled jobs support

#### AWS Lambda (Serverless)
- Pay-per-use pricing
- EventBridge for scheduling
- More complex setup

## 📁 Output Structure

```
outputs/
├── snapshots/           # Daily job snapshots
│   ├── 2025-08-24.csv  # Today's complete data
│   └── ...
├── events/              # Change events log
│   ├── 2025-08-24.csv  # Today's changes
│   └── ...
└── registry/            # Current job registry
    ├── current_jobs.csv # Active jobs CSV
    └── current_jobs.json # Active jobs JSON
```

## 🔍 Testing

Run the test suite to validate open career posts:

```bash
python -m unittest -v tests/test_open_posts.py
```

This will:
- Load today's snapshot (or latest available)
- Filter for open (non-closed) positions
- Print a compact review of each open role

## 📈 Monitoring

### GitHub Actions Summary
Each run creates a summary with:
- Total jobs collected
- Events detected
- Links to output files

### Repository Activity
- Daily commits with job data
- Commit messages show job counts
- Easy to track changes over time

## 🚨 Troubleshooting

### Common Issues

1. **Rate limiting**: Scrapers include delays between requests
2. **API changes**: Some companies update their job board URLs
3. **Authentication**: Some platforms require API keys

### Debug Mode

```bash
python run_scraper.py --verbose
```

### Manual Testing

```bash
# Test specific scraper
python -c "
from scrapers.greenhouse_scraper import GreenhouseScraper
import asyncio

async def test():
    scraper = GreenhouseScraper('test', 'Test Company', 'https://example.com')
    async with scraper:
        jobs = await scraper.scrape_jobs()
        print(f'Found {len(jobs)} jobs')

asyncio.run(test())
"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new scrapers or improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Please check individual company terms of service for job board usage.

## 🔗 Links

- **Latest Outputs**: Check the `outputs/` directory
- **Workflow Status**: GitHub Actions tab
- **Issues**: GitHub Issues for bugs/feature requests

---

*Built with ❤️ for the AI community*