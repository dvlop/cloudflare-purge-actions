FROM python:3.12-alpine

LABEL maintainer="dvlop"
LABEL org.opencontainers.image.source="https://github.com/dvlop/cloudflare-purge-actions"
LABEL org.opencontainers.image.description="GitHub Action to purge Cloudflare cache"

RUN pip install --no-cache-dir requests

COPY app.py /app/app.py

ENTRYPOINT ["python", "/app/app.py"]
