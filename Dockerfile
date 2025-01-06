FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install firefox
RUN playwright install-deps firefox

# Copy the rest of the application
COPY . .

# Default command
CMD ["python3", "main.py"] 
