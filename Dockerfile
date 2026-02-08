FROM python:3.11-slim

WORKDIR /miner

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy miner script
COPY miner.py .

# Make script executable
RUN chmod +x miner.py

# Default command
ENTRYPOINT ["python3", "miner.py"]
CMD ["--config", "config.json"]
