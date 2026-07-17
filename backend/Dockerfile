FROM python:3.11-slim

WORKDIR /app

# mdbtools: ler arquivos Access (.mdb) do sistema antigo (funciona em Linux/Docker,
# igual em hosts Windows e Linux pois o container é sempre Linux)
RUN apt-get update && apt-get install -y --no-install-recommends mdbtools \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY ca-bundle.crt* /root/.ccr/

RUN if [ -f /root/.ccr/ca-bundle.crt ]; then \
      pip install --cert /root/.ccr/ca-bundle.crt --no-cache-dir -r requirements.txt; \
    else \
      pip install --no-cache-dir -r requirements.txt; \
    fi

COPY . .

CMD ["python", "main.py"]
