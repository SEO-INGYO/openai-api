FROM python:3.12-slim

WORKDIR /app

COPY . /app/

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/entrypoint.sh /app/wait-for-it.sh

ENTRYPOINT ["./entrypoint.sh"]