"""Parser for different request formats in the tracking system."""
from typing import Dict, Tuple
from urllib.parse import parse_qs, urlparse

class RequestParser:
    """Parser for different request formats in the tracking system."""
    
    def parse_v1_request(self, json_data: Dict) -> Tuple[str, Dict]:
        """
        Parse V1 pixel request format.
        
        Args:
            json_data: The JSON data from the request
            
        Returns:
            Tuple[str, Dict]: Event name and AppLovin/Axon data
        """
        event_name = json_data.get('name', '')
        applovin_data = json_data.get('applovin', {})
        if not applovin_data:
            applovin_data = json_data.get('axon', {})
        return event_name, applovin_data

    def parse_v2_request(self, json_data: Dict) -> Tuple[str, str, str]:
        """
        Parse V2 pixel request format.
        
        Args:
            json_data: The JSON data from the request
            
        Returns:
            Tuple[str, str, str]: Event name, art value, and event ID
        """
        applovin_data = json_data.get('applovin', {})
        event_data = json_data.get('event', {})
        event_name = event_data.get('name', '')
        request_art = applovin_data.get('art', '')
        request_event_id = applovin_data.get('eventId', '')
        return event_name, request_art, request_event_id

    def parse_url_parameters(self, url: str) -> Tuple[str, str]:
        """
        Parse URL parameters for tracking.
        
        Args:
            url: The URL to parse
            
        Returns:
            Tuple[str, str]: Art value and event ID from URL parameters
        """
        parsed_url = urlparse(url)
        url_params = parse_qs(parsed_url.query)
        return url_params.get('alart', [''])[0], url_params.get('aleid', [''])[0] 