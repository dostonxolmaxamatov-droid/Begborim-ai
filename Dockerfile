FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY server/ ./
ENV PYTHONUNBUFFERED=1 BIND=0.0.0.0 PORT=8080 SHIRIN_DB=/data/shirin.sqlite3 SHIRIN_MEDIA=/data/media
EXPOSE 8080
CMD ["python", "server.py"]
