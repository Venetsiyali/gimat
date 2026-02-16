"""
Base Scraper Class
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime
import asyncio


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers
    """
    
    def __init__(self, name: str):
        self.name = name
        self.last_scrape = None
    
    @abstractmethod
    async def scrape(self) -> List[Dict]:
        """
        Scrape data from source
        
        Returns:
            List of observation dicts
        """
        pass
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()
    
    async def run_periodic(self, interval_seconds: int = 3600):
        """
        Run scraper periodically
        
        Args:
            interval_seconds: Scraping interval
        """
        while True:
            print(f"[{self.name}] Starting scrape...")
            data = await self.scrape()
            self.last_scrape = datetime.now()
            
            print(f"[{self.name}] Scraped {len(data)} records")
            
            # Wait for next interval
            await asyncio.sleep(interval_seconds)


# ==========================================
# Adaptive Scraping Strategy
# ==========================================

class AdaptiveScraper:
    """
    Adaptive scraping with retry logic and rate limiting
    """
    
    def __init__(self, scraper: BaseScraper):
        self.scraper = scraper
        self.retry_count = 3
        self.rate_limit_delay = 5  # seconds
    
    async def scrape_with_retry(self) -> List[Dict]:
        """
        Scrape with retry logic
        
        Returns:
            Scraped data
        """
        for attempt in range(self.retry_count):
            try:
                data = await self.scraper.scrape()
                return data
            
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(self.rate_limit_delay)
                else:
                    print(f"All retry attempts failed for {self.scraper.name}")
                    return []


# ==========================================
# Scraper Scheduler
# ==========================================

class ScraperScheduler:
    """
    Schedule multiple scrapers
    """
    
    def __init__(self):
        self.scrapers = []
    
    def add_scraper(self, scraper: BaseScraper, interval: int):
        """
        Add scraper to schedule
        
        Args:
            scraper: Scraper instance
            interval: Scraping interval in seconds
        """
        self.scrapers.append({
            'scraper': scraper,
            'interval': interval
        })
    
    async def run_all(self):
        """Run all scrapers concurrently"""
        tasks = []
        
        for item in self.scrapers:
            task = item['scraper'].run_periodic(item['interval'])
            tasks.append(task)
        
        await asyncio.gather(*tasks)
