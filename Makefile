.PHONY: all install test clean run run-static run-no-intercept run-quick run-custom matrix help docker-build docker-run docker-static docker-no-intercept docker-quick docker-custom docker-shell analyze

PYTHON = python3
VENV = .venv
PIP = $(VENV)/bin/pip
PYTHON_VENV = $(VENV)/bin/python
PYTHONPATH = PYTHONPATH=$(shell pwd)

# Output directory
OUT_DIR = out
RESULTS_FILE = $(OUT_DIR)/analysis_results.json
MATRIX_FILE = $(OUT_DIR)/matrix.md

# Docker settings
DOCKER_IMAGE = shopanalyzer
CONTAINER_NAME = shopanalyzer
DOCKER_RUN = docker run --rm \
	--name $(CONTAINER_NAME) \
	-v $(shell pwd):/app/data \
	-w /app

# Default target - run static analysis and generate matrix
analyze: docker-run docker-matrix

# Create virtual environment and dependencies
install:
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(PIP) install -r requirements.txt

# Ensure output directory exists
$(OUT_DIR):
	mkdir -p $(OUT_DIR)

# Run tests (if you have any)
test:
	$(PYTHONPATH) $(PYTHON_VENV) -m pytest tests/

# Clean up generated files and virtual environment
clean:
	rm -rf $(VENV) __pycache__ .pytest_cache $(OUT_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	docker rm -f $(CONTAINER_NAME) 2>/dev/null || true
	docker rmi $(DOCKER_IMAGE) 2>/dev/null || true

# Default run mode - full analysis with request interception
run: $(OUT_DIR)
	$(PYTHONPATH) $(PYTHON_VENV) main.py --output-file $(RESULTS_FILE)

# Static analysis only mode
run-static: $(OUT_DIR)
	$(PYTHONPATH) $(PYTHON_VENV) main.py --static-only --output-file $(RESULTS_FILE)

# Run without request interception
run-no-intercept: $(OUT_DIR)
	$(PYTHONPATH) $(PYTHON_VENV) main.py --no-intercept --output-file $(RESULTS_FILE)

# Quick run with shorter wait time
run-quick: $(OUT_DIR)
	$(PYTHONPATH) $(PYTHON_VENV) main.py --wait-time 1.0 --output-file $(RESULTS_FILE)

# Custom run with configurable options
# Usage: make run-custom SITES=custom.json OUTPUT=results.json WAIT=3.0
run-custom: $(OUT_DIR)
	$(PYTHONPATH) $(PYTHON_VENV) main.py \
		$(if $(SITES),--sites-file $(SITES),) \
		--output-file $(or $(OUTPUT),$(RESULTS_FILE)) \
		$(if $(WAIT),--wait-time $(WAIT),) \
		$(if $(STATIC),--static-only,) \
		$(if $(NO_INTERCEPT),--no-intercept,)

# Generate markdown matrix from analysis results
matrix: $(OUT_DIR)
	$(PYTHONPATH) $(PYTHON_VENV) src/utils/gen_matrix.py \
		--input-file $(RESULTS_FILE) \
		--output-file $(MATRIX_FILE)

# Docker targets
docker-build:
	docker build -t $(DOCKER_IMAGE) .

# Docker run targets (require docker-build first)
docker-run: docker-build $(OUT_DIR)
	$(DOCKER_RUN) $(DOCKER_IMAGE) python3 main.py \
		--sites-file /app/data/sites.json \
		--output-file /app/data/$(RESULTS_FILE)

docker-static: docker-build $(OUT_DIR)
	$(DOCKER_RUN) $(DOCKER_IMAGE) python3 main.py \
		--static-only \
		--sites-file /app/data/sites.json \
		--output-file /app/data/$(RESULTS_FILE)

docker-no-intercept: docker-build $(OUT_DIR)
	$(DOCKER_RUN) $(DOCKER_IMAGE) python3 main.py \
		--no-intercept \
		--sites-file /app/data/sites.json \
		--output-file /app/data/$(RESULTS_FILE)

docker-quick: docker-build $(OUT_DIR)
	$(DOCKER_RUN) $(DOCKER_IMAGE) python3 main.py \
		--wait-time 1.0 \
		--sites-file /app/data/sites.json \
		--output-file /app/data/$(RESULTS_FILE)

# Run custom configuration in Docker
# Usage: make docker-custom SITES=custom.json OUTPUT=results.json WAIT=3.0 STATIC=1 NO_INTERCEPT=1
docker-custom: docker-build $(OUT_DIR)
	$(DOCKER_RUN) $(DOCKER_IMAGE) python3 main.py \
		--sites-file /app/data/$(or $(SITES),sites.json) \
		--output-file /app/data/$(or $(OUTPUT),$(RESULTS_FILE)) \
		$(if $(WAIT),--wait-time $(WAIT),) \
		$(if $(STATIC),--static-only,) \
		$(if $(NO_INTERCEPT),--no-intercept,)

# Generate matrix in Docker
docker-matrix: docker-build $(OUT_DIR)
	$(DOCKER_RUN) $(DOCKER_IMAGE) python3 src/utils/gen_matrix.py \
		--input-file /app/data/$(RESULTS_FILE) \
		--output-file /app/data/$(MATRIX_FILE)

# Open an interactive shell in the container
docker-shell: docker-build
	$(DOCKER_RUN) -it $(DOCKER_IMAGE) /bin/bash

# Show help
help:
	@echo "Available targets:"
	@echo "Local targets:"
	@echo "  make install         - Create virtual environment and install dependencies"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean up generated files and virtual environment"
	@echo "  make run            - Run full analysis (default mode)"
	@echo "  make run-static     - Run static analysis only"
	@echo "  make run-no-intercept - Run without request interception"
	@echo "  make run-quick      - Quick run with 1s wait time"
	@echo "  make matrix         - Generate markdown matrix from analysis results"
	@echo "  make run-custom     - Run with custom options"
	@echo ""
	@echo "Docker targets:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run full analysis in Docker"
	@echo "  make docker-static  - Run static analysis in Docker"
	@echo "  make docker-no-intercept - Run without request interception in Docker"
	@echo "  make docker-quick   - Quick run in Docker"
	@echo "  make docker-custom  - Run with custom options in Docker"
	@echo "  make docker-matrix  - Generate matrix from results in Docker"
	@echo "  make docker-shell   - Open interactive shell in Docker container"
	@echo ""
	@echo "Custom options:"
	@echo "  SITES=file.json   - Custom sites file"
	@echo "  OUTPUT=out.json   - Custom output file"
	@echo "  WAIT=3.0         - Custom wait time"
	@echo "  STATIC=1         - Enable static mode"
	@echo "  NO_INTERCEPT=1   - Disable request interception"
	@echo ""
	@echo "Output files will be created in the '$(OUT_DIR)' directory" 
