#!/usr/bin/env python3
"""Generate a markdown matrix from analysis results."""
import json
import argparse
from pathlib import Path
from typing import Dict, List

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate markdown matrix from analysis results')
    parser.add_argument('--input-file', default='analysis_results.json',
                      help='Path to analysis results file')
    parser.add_argument('--output-file', default='matrix.md',
                      help='Path to output markdown file')
    return parser.parse_args()

def load_results(file_path: str) -> List[Dict]:
    """Load analysis results from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def bool_to_mark(value: bool) -> str:
    """Convert boolean to checkmark or x mark."""
    return '✅' if value else '❌'

def generate_matrix(results: List[Dict]) -> str:
    """Generate markdown matrix from results."""
    # Headers
    headers = [
        'Site',
        'Shopify',
        'Headless',
        'Axon',
        'GTM',
        'GA',
        'GA4',
        'Land',
        'Page View',
        'Page Viewed',
        'ALEID',
        'ALART',
        'Axon Reqs',
        'ALBSS Reqs',
        'AppLovin Reqs'
    ]
    
    # Build header row
    matrix = [
        '# Site Analysis Matrix\n',
        '| ' + ' | '.join(headers) + ' |',
        '|' + '|'.join(['---' for _ in headers]) + '|'
    ]
    
    # Build data rows
    for result in results:
        row = [
            result['site'],
            bool_to_mark(result.get('is_shopify', False)),
            bool_to_mark(result.get('is_headless_shopify', False)),
            bool_to_mark(result.get('has_axon', False)),
            bool_to_mark(result.get('has_gtm', False)),
            bool_to_mark(result.get('has_ga', False)),
            bool_to_mark(result.get('has_ga4', False)),
            bool_to_mark(result.get('has_land_event', False)),
            bool_to_mark(result.get('has_page_view_event', False)),
            bool_to_mark(result.get('has_page_viewed_event', False)),
            bool_to_mark(result.get('has_matching_aleid', False)),
            bool_to_mark(result.get('has_matching_alart', False)),
            str(result.get('has_axon_ai_requests', 0)),
            str(result.get('has_albss_requests', 0)),
            str(result.get('has_applovin_requests', 0))
        ]
        matrix.append('| ' + ' | '.join(row) + ' |')
    
    # Add summary section
    matrix.extend([
        '\n## Summary\n',
        '- ✅ = Feature detected',
        '- ❌ = Feature not detected',
        '- Numbers indicate request count',
        '\n## Notes\n',
        '- Shopify: Traditional Shopify implementation',
        '- Headless: Headless Shopify implementation',
        '- Axon: Axon pixel detected',
        '- GTM: Google Tag Manager',
        '- GA: Universal Analytics',
        '- GA4: Google Analytics 4',
        '- Land/Page View/Page Viewed: Tracking events',
        '- ALEID/ALART: Parameter matching',
        '- Reqs: Network requests count'
    ])
    
    return '\n'.join(matrix)

def main():
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_args()
        
        # Load results
        results = load_results(args.input_file)
        
        # Generate matrix
        matrix = generate_matrix(results)
        
        # Create output directory if it doesn't exist
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(matrix)
        
        print(f"Matrix generated successfully: {output_path}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found. Run the analysis first.")
    except Exception as e:
        print(f"Error generating matrix: {str(e)}")

if __name__ == '__main__':
    main() 