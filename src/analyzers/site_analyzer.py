"""Site analysis functionality for tracking system."""
from typing import Dict, List, Optional
import json
import logging
import sys
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

# Import constants with error handling
try:
    from src.constants import (
        TRACKING_INDICATORS,
        DOMAINS_OF_INTEREST,
        HEADLESS_SHOPIFY_INDICATORS
    )
    logger.debug("Successfully imported constants")
except ImportError as e:
    logger.error(f"Failed to import constants: {e}")
    logger.error(f"Python path: {sys.path}")
    raise

from src.parsers.request_parser import RequestParser

class SiteAnalyzer:
    """Analyzes site content and network requests for tracking implementations."""
    
    def __init__(self):
        self.reset_flags()
        self.request_parser = RequestParser()
        self.logger = logging.getLogger(__name__)
        
        # Verify constants are available
        if not DOMAINS_OF_INTEREST:
            raise ImportError("DOMAINS_OF_INTEREST is not properly imported")

    def reset_flags(self):
        """Initialize/reset all tracking flags"""
        # Stage 1: Content indicators
        self.content_indicators = {
            'shopify': False,
            'headless_shopify': False,
            'axon': False,
            'gtm': False,
            'ga': False,
            'ga4': False
        }
        
        # Stage 2: Network requests
        self.network_requests = {
            'axon_ai': [],
            'albss': [],
            'applovin': [],
            'tracking': [],
            'shopify_api': []  # Track Shopify API calls
        }
        
        # Stage 3: Event tracking
        self.events = {
            'land': False,
            'page_view': False,
            'page_viewed': False
        }

        # Stage 3: Parameter matching
        self.parameter_matches = {
            'aleid': False,
            'alart': False
        }

        # Headless Shopify specific indicators
        self.headless_indicators = {
            'api_calls': False,
            'storefront_api': False,
            'hydrogen': False,
            'buy_sdk': False
        }

    def analyze_static(self, site_name: str, url: str) -> Dict:
        """
        Perform static analysis of a site URL without browser interaction.
        
        Args:
            site_name: Name of the site being analyzed
            url: URL to analyze
            
        Returns:
            Dict: Analysis results
        """
        self.reset_flags()
        
        # Parse URL
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Check domain
        domain = parsed_url.netloc.lower()
        
        # Check for Shopify indicators in domain
        if '.myshopify.com' in domain or 'shopify.com' in domain:
            self.content_indicators['shopify'] = True
        
        # Check for tracking parameters
        if 'aleid' in query_params:
            self.parameter_matches['aleid'] = True
        if 'alart' in query_params:
            self.parameter_matches['alart'] = True
            
        # Check for common tracking parameters
        tracking_params = {
            'utm_source': False,
            'utm_medium': False,
            'utm_campaign': False
        }
        
        for param in tracking_params:
            if param in query_params:
                tracking_params[param] = True
                if query_params[param][0].lower() == 'applovin':
                    self.events['land'] = True
        
        # Prepare results
        results = {
            'site': site_name,
            'url': url,
            'analysis_type': 'static',
            'domain': domain,
            'tracking_parameters': {
                'aleid': self.parameter_matches['aleid'],
                'alart': self.parameter_matches['alart'],
                **tracking_params
            },
            'indicators': {
                'shopify': self.content_indicators['shopify'],
                'tracking_present': any(tracking_params.values()) or 
                                 self.parameter_matches['aleid'] or 
                                 self.parameter_matches['alart']
            },
            'events': {
                'land': self.events['land']
            }
        }
        
        return results

    def check_page_content(self, page) -> None:
        """
        Stage 1: Check page content for various tracking scripts.
        
        Args:
            page: The Playwright page object
        """
        try:
            content = page.content().lower()
            
            # Check each indicator
            for indicator, patterns in TRACKING_INDICATORS.items():
                self.content_indicators[indicator] = any(
                    pattern.lower() in content for pattern in patterns
                )
            
            # Check for headless Shopify indicators in scripts
            self._check_headless_shopify_scripts(page)
            
            # Check meta tags for headless Shopify
            self._check_headless_shopify_meta_tags(page)
                
        except Exception as e:
            self.logger.warning(f"Error during content checks: {str(e)}")

    def _check_headless_shopify_scripts(self, page) -> None:
        """
        Check for headless Shopify script patterns.
        
        Args:
            page: The Playwright page object
        """
        try:
            # Track number of headless indicators found
            headless_indicators_found = 0
            
            # Check script sources and content
            scripts = page.query_selector_all('script')
            for script in scripts:
                src = script.get_attribute('src') or ''
                
                # Check for Hydrogen framework
                if '@shopify/hydrogen' in src:
                    self.headless_indicators['hydrogen'] = True
                    headless_indicators_found += 1
                
                # Check for Storefront API
                if '@shopify/storefront-api' in src:
                    self.headless_indicators['storefront_api'] = True
                    headless_indicators_found += 1
                
                # Check for Buy SDK
                if 'shopify-buy' in src:
                    self.headless_indicators['buy_sdk'] = True
                    headless_indicators_found += 1
                
                # Check inline scripts
                try:
                    script_content = script.inner_text().lower()
                    for pattern in HEADLESS_SHOPIFY_INDICATORS['script_patterns']:
                        if pattern.lower() in script_content:
                            headless_indicators_found += 1
                            break
                except:
                    pass  # Skip if can't get script content
            
            # Only mark as headless if we found multiple indicators
            if headless_indicators_found >= 2:
                self.content_indicators['headless_shopify'] = True
                    
        except Exception as e:
            self.logger.warning(f"Error checking headless Shopify scripts: {str(e)}")

    def _check_headless_shopify_meta_tags(self, page) -> None:
        """
        Check for headless Shopify meta tags.
        
        Args:
            page: The Playwright page object
        """
        try:
            meta_indicators_found = 0
            meta_tags = page.query_selector_all('meta')
            for meta in meta_tags:
                name = meta.get_attribute('name') or ''
                content = meta.get_attribute('content') or ''
                
                for pattern in HEADLESS_SHOPIFY_INDICATORS['meta_tags']:
                    if pattern.lower() in name.lower() or pattern.lower() in content.lower():
                        meta_indicators_found += 1
            
            # Only contribute to headless detection if we found multiple meta indicators
            if meta_indicators_found >= 2:
                self.content_indicators['headless_shopify'] = True
                        
        except Exception as e:
            print(f"Warning: Error checking headless Shopify meta tags: {str(e)}")

    def check_request(self, request):
        """
        Check and process incoming requests.
        
        Args:
            request: The request object from Playwright
        """
        url = request.url.lower()
        
        # Check for Shopify API calls
        self._check_shopify_api_request(request)
        
        # Process requests based on domains of interest
        for domain, info in DOMAINS_OF_INTEREST.items():
            if domain in url:
                request_info = {
                    'url': url,
                    'method': request.method,
                    'type': request.resource_type,
                    'critical': info['critical']
                }
                
                # Store request in appropriate category
                if domain == 'applovin.com':
                    self.network_requests['applovin'].append(request_info)
                    self.logger.info("AppLovin Request Detected:")
                elif domain == 'axon.ai':
                    self.network_requests['axon_ai'].append(request_info)
                    self.logger.info("Axon.ai Request Detected:")
                elif domain == 'albss.com':
                    self.network_requests['albss'].append(request_info)
                    self.logger.info("ALBSS Request Detected:")
                
                self.logger.info(f"  URL: {url}")
                self.logger.info(f"  Method: {request.method}")
                self.logger.info(f"  Type: {request.resource_type}")
                self.logger.info(f"  Critical: {info['critical']}")
        
        # Check AppLovin pixel requests
        if 'https://b.applovin.com/' in url and 'pixel' in url and request.method == 'POST':
            self._process_pixel_request(request)

    def _check_shopify_api_request(self, request):
        """
        Check if request is a Shopify API call.
        
        Args:
            request: The request object from Playwright
        """
        url = request.url.lower()
        headers = request.headers
        api_indicators = 0
        
        # Check URL patterns
        for endpoint in HEADLESS_SHOPIFY_INDICATORS['api_endpoints']:
            if endpoint.lower() in url:
                api_indicators += 1
                self.headless_indicators['api_calls'] = True
                self._log_shopify_api_request(request)
                break
        
        # Check headers
        for header in HEADLESS_SHOPIFY_INDICATORS['request_headers']:
            if header.lower() in str(headers).lower():
                api_indicators += 1
                self.headless_indicators['api_calls'] = True
                self._log_shopify_api_request(request)
                break
        
        # Only mark as headless if we found multiple API indicators
        if api_indicators >= 2:
            self.content_indicators['headless_shopify'] = True

    def _log_shopify_api_request(self, request):
        """
        Log Shopify API request details.
        
        Args:
            request: The request object from Playwright
        """
        request_info = {
            'url': str(request.url),
            'method': request.method,
            'type': request.resource_type,
            'headers': dict(request.headers)
        }
        self.network_requests['shopify_api'].append(request_info)
        self.logger.info("Shopify API Request Detected:")
        self.logger.info(f"  URL: {request.url}")
        self.logger.info(f"  Method: {request.method}")
        self.logger.info(f"  Type: {request.resource_type}")

    def _process_pixel_request(self, request):
        """
        Process AppLovin pixel requests.
        
        Args:
            request: The request object from Playwright
        """
        try:
            current_url = request.frame.page.url
            url_alart, url_aleid = self.request_parser.parse_url_parameters(current_url)
            print(f"URL Parameters: alart={url_alart}, aleid={url_aleid}")

            post_data = request.post_data
            if not post_data:
                return

            json_data = json.loads(post_data)
            url = request.url
            
            if '/shopify/v2/pixel' in url or '/v2/pixel' in url:
                event_name, art, event_id = self.request_parser.parse_v2_request(json_data)
                self.log_event_data(event_name, url, art, event_id, url_alart, url_aleid)
            else:
                event_name, axon_data = self.request_parser.parse_v1_request(json_data)
                self.log_event_data(
                    event_name, url, 
                    axon_data.get('art', ''), 
                    axon_data.get('eventId', ''),
                    url_alart, url_aleid
                )
                    
        except Exception as e:
            print(f"Warning: Error parsing AppLovin pixel request: {str(e)}")

    def log_event_data(self, event_name, version, art, event_id, url_alart, url_aleid):
        """
        Log event data and check for parameter matches.
        
        Args:
            event_name: Name of the event
            version: API version used
            art: Art value from request
            event_id: Event ID from request
            url_alart: Art value from URL
            url_aleid: Event ID from URL
        """
        # Check event types
        if event_name == 'land':
            self.events['land'] = True
        elif event_name == 'page_view':
            self.events['page_view'] = True
        elif event_name == 'page_viewed':
            self.events['page_viewed'] = True
        
        # Update match flags for valid values
        if art and url_alart:
            if art == url_alart:
                self.parameter_matches['alart'] = True
        if event_id and url_aleid:
            if event_id == url_aleid:
                self.parameter_matches['aleid'] = True
        
        # Log the event details
        request_info = f"Axon Event: {event_name}"
        self.logger.info(request_info)
        self.logger.info(f"    API Version: {version}")
        self.logger.info(f"    alart match: {'✅' if art == url_alart else '❌'} ({art} vs {url_alart})")
        self.logger.info(f"    aleid match: {'✅' if event_id == url_aleid else '❌'} ({event_id} vs {url_aleid})")
        
        self.network_requests['tracking'].append(request_info)

    def check_shopify_indicators(self, page, response: Optional[Dict] = None) -> None:
        """
        Check various indicators of Shopify usage.
        
        Args:
            page: The Playwright page object
            response: Optional response object from page load
        """
        try:
            # Check response headers if available
            if response and 'shopify' in response.headers.get('server', '').lower():
                self.content_indicators['shopify'] = True
                return

            # Check URL and DOM elements
            url = page.url
            if 'myshopify.com' in url:
                self.content_indicators['shopify'] = True
                return

            self.content_indicators['shopify'] = any([
                page.query_selector('link[href*="shopify"]') is not None,
                page.query_selector('script[src*="shopify"]') is not None,
                'Shopify.shop' in page.content()
            ])
        except Exception as e:
            print(f"Warning: Error checking Shopify indicators: {str(e)}")

    def get_results(self, site_name: str, site_url: str, warning: str = None) -> Dict:
        """
        Generate results dictionary for the current analysis.
        
        Args:
            site_name: Name of the site
            site_url: URL of the site
            warning: Optional warning message
            
        Returns:
            Dict: Analysis results
        """
        results = {
            "site": site_name,
            "url": site_url,
            "is_shopify": self.content_indicators['shopify'],
            "is_headless_shopify": self.content_indicators['headless_shopify'],
            "headless_shopify_details": {
                "uses_storefront_api": self.headless_indicators['storefront_api'],
                "uses_hydrogen": self.headless_indicators['hydrogen'],
                "uses_buy_sdk": self.headless_indicators['buy_sdk'],
                "has_api_calls": self.headless_indicators['api_calls'],
                "api_calls_count": len(self.network_requests['shopify_api'])
            },
            "has_axon": self.content_indicators['axon'],
            "has_gtm": self.content_indicators['gtm'],
            "has_ga": self.content_indicators['ga'],
            "has_ga4": self.content_indicators['ga4'],
            "has_land_event": self.events['land'],
            "has_page_view_event": self.events['page_view'],
            "has_page_viewed_event": self.events['page_viewed'],
            "has_axon_ai_requests": len(self.network_requests['axon_ai']),
            "has_albss_requests": len(self.network_requests['albss']),
            "has_matching_aleid": self.parameter_matches['aleid'],
            "has_matching_alart": self.parameter_matches['alart'],
            "has_applovin_requests": len(self.network_requests['applovin'])
        }
        if warning:
            results["warning"] = warning
        return results

    def print_results(self, site_name: str) -> None:
        """
        Print the analysis results for a site.
        
        Args:
            site_name: Name of the site
        """
        self.logger.info(f"\nResults for {site_name}:")
        self.logger.info(f"  Shopify: {'✅' if self.content_indicators['shopify'] else '❌'}")
        self.logger.info(f"  Headless Shopify: {'✅' if self.content_indicators['headless_shopify'] else '❌'}")
        
        if self.content_indicators['headless_shopify']:
            self.logger.info("    Headless Implementation Details:")
            self.logger.info(f"    - Storefront API: {'✅' if self.headless_indicators['storefront_api'] else '❌'}")
            self.logger.info(f"    - Hydrogen Framework: {'✅' if self.headless_indicators['hydrogen'] else '❌'}")
            self.logger.info(f"    - Buy SDK: {'✅' if self.headless_indicators['buy_sdk'] else '❌'}")
            self.logger.info(f"    - API Calls: {'✅' if self.headless_indicators['api_calls'] else '❌'} ({len(self.network_requests['shopify_api'])} calls)")
        
        self.logger.info(f"  Axon Pixel: {'✅' if self.content_indicators['axon'] else '❌'}")
        self.logger.info(f"  Google Tag Manager: {'✅' if self.content_indicators['gtm'] else '❌'}")
        self.logger.info(f"  Google Analytics: {'✅' if self.content_indicators['ga'] else '❌'}")
        self.logger.info(f"  GA4: {'✅' if self.content_indicators['ga4'] else '❌'}")
        
        self.logger.info("\nTracking Events:")
        self.logger.info(f"  Land Event: {'✅' if self.events['land'] else '❌'}")
        self.logger.info(f"  Page View Event: {'✅' if self.events['page_view'] else '❌'}")
        self.logger.info(f"  Page Viewed Event: {'✅' if self.events['page_viewed'] else '❌'}")
        self.logger.info(f"  Matching ALEID: {'✅' if self.parameter_matches['aleid'] else '❌'}")
        self.logger.info(f"  Matching ALART: {'✅' if self.parameter_matches['alart'] else '❌'}")
        
        self.logger.info("\nNetwork Requests:")
        self.logger.info(f"  Axon.ai Requests: {'✅' if len(self.network_requests['axon_ai']) else '❌'} ({len(self.network_requests['axon_ai'])} requests)")
        self.logger.info(f"  ALBSS Requests: {'✅' if len(self.network_requests['albss']) else '❌'} ({len(self.network_requests['albss'])} requests)")
        self.logger.info(f"  AppLovin Requests: {'✅' if len(self.network_requests['applovin']) else '❌'} ({len(self.network_requests['applovin'])} requests)")
        
        if self.network_requests['tracking']:
            self.logger.info("\n  Tracking Requests Found:")
            for req in self.network_requests['tracking']:
                self.logger.info(f"    • {req}")
                
        if self.network_requests['axon_ai']:
            self.logger.info("\n  Axon.ai Requests Found:")
            for req in self.network_requests['axon_ai']:
                self.logger.info(f"    • {req['method']} {req['url']} ({req['type']})")
                
        if self.network_requests['albss']:
            self.logger.info("\n  ALBSS Requests Found:")
            for req in self.network_requests['albss']:
                self.logger.info(f"    • {req['method']} {req['url']} ({req['type']})")
                
        if self.network_requests['shopify_api']:
            self.logger.info("\n  Shopify API Requests Found:")
            for req in self.network_requests['shopify_api']:
                self.logger.info(f"    • {req['method']} {req['url']} ({req['type']})") 