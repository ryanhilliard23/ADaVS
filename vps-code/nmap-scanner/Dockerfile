FROM python:3.11-slim

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      nmap iproute2 \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash scanner
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY main.py /app/main.py

USER scanner
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]