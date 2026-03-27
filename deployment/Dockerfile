FROM python:3.12-slim

WORKDIR /app

# Install dependencies first to leverage Docker layer cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY app/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3695"]
