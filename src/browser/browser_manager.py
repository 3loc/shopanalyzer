"""Browser management functionality for the site testing system."""
from typing import Dict, List, Optional, Tuple, Set
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import time

from src.constants import BROWSER_SETTINGS, PAGE_LOAD_TIMEOUT, NETWORK_IDLE_TIMEOUT, DOMAINS_OF_INTEREST
from src.utils.request_handlers import is_domain_of_interest, create_failed_request_info

class BrowserManager:
    """Manages browser interactions and request monitoring."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.failed_requests: List[Dict] = []
        self.pending_requests: Set[str] = set()
        
    def initialize_browser(self):
        """
        Initialize browser with required settings.
        
        Returns:
            playwright: The initialized playwright instance
        """
        playwright = sync_playwright().start()
        self.browser = playwright.firefox.launch(**BROWSER_SETTINGS)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        
        # Set up network monitoring
        self.page.on("request", self._handle_request)
        self.page.on("requestfailed", self._handle_request_failed)
        self.page.on("requestfinished", self._handle_request_finished)
        
        return playwright

    def _handle_request(self, request):
        """
        Track new requests.
        
        Args:
            request: The request object from Playwright
        """
        url = str(request.url)
        self.pending_requests.add(url)

    def _handle_request_failed(self, request):
        """
        Log failed requests with detailed information.
        
        Args:
            request: The request object from Playwright
        """
        url = str(request.url)
        self.pending_requests.discard(url)
        
        is_interesting, is_critical = is_domain_of_interest(url)
        if not is_interesting:
            return
            
        error_text = request.failure or 'Unknown error'
        
        # Only log critical failures for critical domains
        if not is_critical and not any(domain in url.lower() for domain, info 
                                     in DOMAINS_OF_INTEREST.items() 
                                     if info['critical']):
            return
            
        self.failed_requests.append(create_failed_request_info(request, error_text))

    def _handle_request_finished(self, request):
        """
        Track completed requests.
        
        Args:
            request: The request object from Playwright
        """
        url = str(request.url)
        self.pending_requests.discard(url)

    def load_page(self, url: str) -> Tuple[Optional[str], Optional[Dict], List[Dict]]:
        """
        Load a page and handle potential errors.
        
        Args:
            url: The URL to load
            
        Returns:
            Tuple[Optional[str], Optional[Dict], List[Dict]]: Warning message, response object, and failed requests
        """
        warning = None
        response = None
        self.failed_requests = []
        
        try:
            # Clear pending requests
            self.pending_requests.clear()
            
            response = self.page.goto(
                url, 
                wait_until='domcontentloaded', 
                timeout=PAGE_LOAD_TIMEOUT
            )
            print("Initial page load complete")
            
            try:
                self.page.wait_for_load_state('networkidle', timeout=NETWORK_IDLE_TIMEOUT)
                print("Network idle achieved")
                
            except Exception as e:
                # Only show pending requests from domains we care about
                important_pending = {
                    url for url in self.pending_requests 
                    if any(domain in url.lower() for domain in DOMAINS_OF_INTEREST.keys())
                }
                
                if important_pending:
                    pending_count = len(important_pending)
                    warning = f"Network idle timeout: {str(e)}. {pending_count} important requests still pending."
                    print(f"Warning: {warning}")
                    print("\nPending Important Requests:")
                    for pending_url in important_pending:
                        print(f"  - {pending_url}")
                    
        except Exception as e:
            warning = f"Page load timeout: {str(e)}"
            print(f"Warning: {warning}")
        
        return warning, response, self.failed_requests

    def close_browser(self):
        """Clean up browser resources."""
        if self.browser:
            self.browser.close() 