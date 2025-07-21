# Base image for API
FROM python:3.10-slim as base

WORKDIR /app
COPY ./ ./

RUN pip install --no-cache-dir -r requirements.txt

# Run migrations and start API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
