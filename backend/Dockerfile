FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY ca-bundle.crt* /root/.ccr/

RUN if [ -f /root/.ccr/ca-bundle.crt ]; then \
      pip install --cert /root/.ccr/ca-bundle.crt --no-cache-dir -r requirements.txt; \
    else \
      pip install --no-cache-dir -r requirements.txt; \
    fi

COPY . .

CMD ["python", "main.py"]
