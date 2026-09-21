FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY server.py montage.py storyboard.py index.html web.js web.css ./
ENV PYTHONUNBUFFERED=1 BIND=0.0.0.0 PORT=8080 BEGBORIM_DB=/data/begborim.sqlite3 BEGBORIM_MEDIA=/data/media
EXPOSE 8080
CMD ["python", "server.py"]
