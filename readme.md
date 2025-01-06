# Shop Analyzer

A tool for analyzing e-commerce sites' tracking implementations. It validates tracking pixels, analytics, and network requests using Playwright for automated browser testing.

## Features

- Automated testing of e-commerce sites
- Network request monitoring and validation
- Static and dynamic analysis modes
- Docker support for containerized execution
- Configurable wait times and test parameters
- Markdown report generation

## Prerequisites

- Python 3.8+
- Make
- Docker (optional, for containerized execution)

## Quick Start

1. Clone the repository
2. Copy and configure your sites:
   ```bash
   cp sites.json.example sites.json
   # Edit sites.json with your target sites
   ```
3. Run the analysis:
   ```bash
   make analyze
   ```

This will:
1. Build and run the Docker container
2. Analyze all sites in `sites.json` and generate analysis results
3. You can then generate a matrix from these results using `make docker-matrix`

## Configuration

### Sites Configuration (sites.json)
```json
{
    "sites": [
        {
            "name": "Example Store",
            "url": "https://example.com/"
        }
    ]
}
```

## Usage

### Basic Commands

```bash
# Run analysis in Docker (recommended)
make analyze

# Local development setup
make install

# Run without Docker
make run

# Quick analysis (1s wait time)
make run-quick

# Static analysis only
make run-static

# Generate matrix from analysis results
make docker-matrix
```

### Advanced Usage

Custom run with options:
```bash
make run-custom SITES=custom.json OUTPUT=results.json WAIT=3.0
```

Docker-based custom run:
```bash
make docker-custom SITES=custom.json OUTPUT=results.json WAIT=3.0
```

### Available Options

- `SITES`: Custom sites configuration file
- `OUTPUT`: Custom output file location
- `WAIT`: Wait time for network requests (seconds)
- `STATIC`: Enable static analysis only
- `NO_INTERCEPT`: Disable request interception

## Output

The tool generates output files in the `out/` directory:

1. Analysis results:
   - `analysis_results.json`: Detailed analysis results from running `make analyze`

2. Optional matrix format:
   - `matrix.md`: Summary matrix in markdown format (generated separately with `make docker-matrix`)

## Development

```bash
# Build Docker image
make docker-build

# Run interactive shell in container
make docker-shell

# Clean all build artifacts
make clean
```
