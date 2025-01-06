"""Main testing orchestration for the site testing system."""
import json
import time
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.constants import DOMAINS_OF_INTEREST
from src.browser.browser_manager import BrowserManager
from src.analyzers.site_analyzer import SiteAnalyzer

@dataclass
class TesterConfig:
    """Configuration for the site tester.
    
    Args:
        sites_file: Path to the sites configuration file
        wait_time: Time to wait for network requests in seconds
        intercept_requests: Whether to intercept and analyze network requests
        static_analysis_only: Whether to only perform static code analysis without browser
        output_file: Path to save analysis results
    """
    sites_file: str = 'sites.json'
    wait_time: float = 5.0
    intercept_requests: bool = True
    static_analysis_only: bool = False
    output_file: str = 'analysis_results.json'

class SiteTester:
    """Orchestrates the testing of sites for tracking implementations."""
    
    def __init__(self, config: Optional[TesterConfig] = None):
        """Initialize the tester.
        
        Args:
            config: Configuration options for the tester
        """
        self.config = config or TesterConfig()
        self.sites_file = Path(self.config.sites_file)
        self.output_file = Path(self.config.output_file)
        self.browser_manager = None if self.config.static_analysis_only else BrowserManager()
        self.analyzer = SiteAnalyzer()
        self.logger = logging.getLogger(__name__)

    def prepare_url(self, url: str) -> str:
        """
        Prepare URL with tracking parameters if needed.
        
        Args:
            url: The URL to test
            
        Returns:
            str: URL with tracking parameters
        """
        if 'aleid=' not in url and 'alart=' not in url:
            separator = '&' if '?' in url else '?'
            url = f"{url}{separator}alart=test_identifier1234&aleid=test_identifier5678"
        return url

    def analyze_single_site(self, site: Dict) -> Dict:
        """
        Analyze a single site and return the results.
        
        Args:
            site: Dictionary containing site information
            
        Returns:
            Dict: Analysis results
        """
        if not isinstance(site, dict) or 'name' not in site or 'url' not in site:
            raise ValueError("Invalid site configuration")

        self.analyzer.reset_flags()
        url = self.prepare_url(site['url'])
        self.logger.info(f"Analyzing: {site['name']} @ {site['url']}")
        
        try:
            if self.config.static_analysis_only:
                self.logger.info("Performing static analysis only...")
                results = self.analyzer.analyze_static(site['name'], url)
            else:
                warning, response, failed_requests = self.browser_manager.load_page(url)
                
                self.logger.info("Stage 1: Checking page content...")
                self.analyzer.check_page_content(self.browser_manager.page)
                self.analyzer.check_shopify_indicators(self.browser_manager.page, response)
                
                if self.config.intercept_requests:
                    self.logger.info("Stage 2: Waiting for remaining network requests...")
                    time.sleep(self.config.wait_time)
                
                results = self.analyzer.get_results(site['name'], url, warning)
                
                if failed_requests:
                    results["failed_requests"] = failed_requests
                    
                self.analyzer.print_results(site['name'])
            
            return results

        except Exception as e:
            self.logger.error(f"Error analyzing {site['name']}: {str(e)}")
            return {
                "site": site['name'],
                "url": url,
                "error": str(e),
                "error_type": type(e).__name__,
                "failed_requests": getattr(self.browser_manager, 'failed_requests', [])
            }

    def run_tests(self) -> List[Dict]:
        """Run tests for all sites in the configuration.
        
        Returns:
            List[Dict]: List of analysis results for each site
        """
        if not self.sites_file.exists():
            raise FileNotFoundError(f"Sites configuration file not found: {self.sites_file}")

        results = []
        playwright = None
        
        try:
            if not self.config.static_analysis_only:
                playwright = self.browser_manager.initialize_browser()
                if self.config.intercept_requests:
                    self.browser_manager.page.on("request", self.analyzer.check_request)

            with open(self.sites_file, 'r') as f:
                config = json.load(f)
                if not isinstance(config, dict) or 'sites' not in config:
                    raise ValueError("Invalid sites.json format")
                sites = config['sites']

            for site in sites:
                results.append(self.analyze_single_site(site))

        finally:
            if not self.config.static_analysis_only:
                self.browser_manager.close_browser()
                if playwright:
                    playwright.stop()

        with open(self.output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Analysis complete! Results saved to {self.output_file}")
        return results 