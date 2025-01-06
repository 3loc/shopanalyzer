"""Main entry point for the site testing system."""
import sys
import logging
import argparse
from src.testers.site_tester import SiteTester, TesterConfig

def parse_args() -> TesterConfig:
    """Parse command line arguments.
    
    Returns:
        TesterConfig: Configuration object based on command line args
    """
    parser = argparse.ArgumentParser(description='Site testing system')
    parser.add_argument('--sites-file', default='sites.json',
                      help='Path to sites configuration file')
    parser.add_argument('--wait-time', type=float, default=5.0,
                      help='Time to wait for network requests in seconds')
    parser.add_argument('--no-intercept', action='store_true',
                      help='Disable request interception')
    parser.add_argument('--static-only', action='store_true',
                      help='Perform static analysis only')
    parser.add_argument('--output-file', default='analysis_results.json',
                      help='Path to save analysis results')
    
    args = parser.parse_args()
    return TesterConfig(
        sites_file=args.sites_file,
        wait_time=args.wait_time,
        intercept_requests=not args.no_intercept,
        static_analysis_only=args.static_only,
        output_file=args.output_file
    )

def main() -> int:
    """Run the site testing system.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        # Set up debug logging
        logging.basicConfig(
            level=logging.DEBUG,  # Change to DEBUG level
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        logger.debug("Starting application")
        
        # Import check
        try:
            from src.constants import DOMAINS_OF_INTEREST
            logger.debug("Successfully imported DOMAINS_OF_INTEREST")
        except ImportError as e:
            logger.error(f"Failed to import DOMAINS_OF_INTEREST: {e}")
            logger.error(f"Python path: {sys.path}")
            return 1
        
        config = parse_args()
        tester = SiteTester(config)
        tester.run_tests()
        return 0
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}", exc_info=True)  # Add full traceback
        return 1

if __name__ == "__main__":
    sys.exit(main()) 