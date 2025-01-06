```
  _______ __                _______             __                        
 |   _   |  |--.-----.-----|   _   .-----.---.-|  .--.--.-----.-----.----.
 |   1___|     |  _  |  _  |.  1   |     |  _  |  |  |  |-- __|  -__|   _|
 |____   |__|__|_____|   __|.  _   |__|__|___._|__|___  |_____|_____|__|  
 |:  1   |           |__|  |:  |   |              |_____|                 
 |::.. . |                 |::.|:. |                                      
 `-------'                 `--- ---'                                      
                                                                          

```
# ShopAnalyzer
A tool for analyzing e-commerce sites, focusing on tracking implementations and analytics integrations. It helps identify platform types, validate tracking parameters, and monitor network requests.

## Overview

ShopAnalyzer examines e-commerce sites for:
- Tracking parameter implementations
- Platform identification
- Analytics integrations
- Network request patterns
- Analysis reports

## Core Functionality

- Static analysis of URLs and tracking parameters
- Platform type detection
- Analytics validation (GTM, GA4, custom pixels)
- Network request monitoring
- Report generation

## Requirements

- Docker Engine 20.10+
- Python 3.10+ (for local development)
- GNU Make

## Installation

Clone the ShopAnalyzer repository and ensure Docker is running. No additional installation is required for Docker-based execution.

## Configuration

Create a `sites.json` file in the project root:
```json
{
    "sites": [
        {
            "name": "Example Store",
            "url": "https://example.com?alart=test123&aleid=test456"
        }
    ]
}
```

See `sites.json.example` for additional configuration examples.

## Usage

### Basic Usage
```bash
make analyze  # Runs analysis suite and generates report
```

### Advanced Options

#### Docker-based Execution
```bash
# Static analysis only
make docker-static

# Custom configuration
make docker-custom SITES=custom.json OUTPUT=results.json WAIT=3.0
```

#### Local Development
```bash
# Run analysis locally
make run-static

# Generate report
make matrix
```

## Output

All analysis artifacts are stored in the `out` directory:
- `analysis_results.json`: Detailed analysis data including tracking parameters, platform detection, and request patterns
- `matrix.md`: Formatted analysis report summarizing findings

## Analysis Components

### Platform Detection
- E-commerce platform identification
- Implementation type detection
- API endpoint patterns
- Integration methods

### Analytics Validation
- Google Tag Manager presence
- Google Analytics 4 implementation
- Universal Analytics legacy code
- Custom tracking pixels

### Request Analysis
- AppLovin tracking requests
- UTM parameter validation
- Custom tracking parameters
- API call patterns

## Make Targets

### Primary Targets
```bash
make analyze          # Full analysis suite
make docker-static    # Static analysis only
make docker-matrix    # Report generation
```

### Development Targets
```bash
make install          # Setup development environment
make test            # Run test suite
make clean           # Clean build artifacts
```

### Configuration Options
```bash
SITES=file.json      # Input configuration
OUTPUT=out.json      # Analysis output
WAIT=3.0            # Request timeout
STATIC=1            # Static analysis mode
NO_INTERCEPT=1      # Disable request interception
```

## Development

Contributions should follow the existing code structure and include appropriate tests. See CONTRIBUTING.md for detailed guidelines.

## Output Format

The analysis generates two files in the `out` directory:

### analysis_results.json
Detailed JSON output containing all analysis data:
```json
{
    "site_name": {
        "url": "https://example.com",
        "platform": {
            "type": "detected_platform",
            "indicators": ["found_indicators"]
        },
        "analytics": {
            "gtm": true,
            "ga4": false
        },
        "tracking": {
            "alart": "test123",
            "aleid": "test456"
        },
        "requests": [
            {
                "url": "request_url",
                "type": "request_type"
            }
        ]
    }
}
```

### matrix.md
A simplified markdown table generated from the analysis results, showing key findings in a matrix format. 
