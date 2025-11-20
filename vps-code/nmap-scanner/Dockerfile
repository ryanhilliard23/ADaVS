FROM python:3.11-slim


RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl unzip iproute2 ca-certificates && \
    rm -rf /var/lib/apt/lists/*


RUN curl -sSL -o /tmp/nuclei.zip \
    "https://github.com/projectdiscovery/nuclei/releases/download/v3.4.10/nuclei_3.4.10_linux_amd64.zip" && \
    unzip /tmp/nuclei.zip -d /tmp/nuclei && \
    mv /tmp/nuclei/nuclei /usr/local/bin/nuclei && \
    chmod +x /usr/local/bin/nuclei && \
    rm -rf /tmp/nuclei /tmp/nuclei.zip


WORKDIR /app
COPY main.py /app/main.py


RUN mkdir -p /home/nuclei/nuclei-templates


ENV HOME=/home/nuclei
ENV NUCLEI_TEMPLATES=/home/nuclei/nuclei-templates
ENV NUCLEI_SKIP_UPDATE=true
ENV NUCLEI_NO_VERSION_CHECK=true
ENV DISABLE_NUCLEI_TEMPLATES_PUBLIC_DOWNLOAD=true
ENV DISABLE_NUCLEI_TEMPLATES_GITHUB_DOWNLOAD=true
ENV DISABLE_NUCLEI_TEMPLATES_GITLAB_DOWNLOAD=true
ENV DISABLE_NUCLEI_TEMPLATES_AWS_DOWNLOAD=true
ENV DISABLE_NUCLEI_TEMPLATES_AZURE_DOWNLOAD=true


RUN pip install --no-cache-dir fastapi uvicorn


COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8001
CMD ["/start.sh"]