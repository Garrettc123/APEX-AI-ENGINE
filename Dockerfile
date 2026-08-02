FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' apexuser
RUN chown -R apexuser:apexuser /app
USER apexuser

EXPOSE 8000

CMD ["uvicorn", "apex.main:app", "--host", "0.0.0.0", "--port", "8000"]
