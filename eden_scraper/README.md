# Eden-DAoC Scraper

Module pour scraper les données du site Eden-DAoC avec authentification Discord.

## Installation

```bash
pip install -r eden_requirements.txt
```

## Utilisation

```python
from eden_scraper import PersistentScraper

scraper = PersistentScraper()
data = scraper.scrape_with_session(url)
```
