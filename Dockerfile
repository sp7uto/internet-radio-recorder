FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg python3 ca-certificates tzdata && rm -rf /var/lib/apt/lists/*
RUN useradd --system --uid 1000 --create-home recorder && mkdir -p /app /config /recordings && chown -R recorder:recorder /app /config /recordings
COPY recorder.py web.py /app/
COPY static /app/static
RUN chmod +x /app/*.py && chown -R recorder:recorder /app
USER recorder
WORKDIR /app
ENTRYPOINT ["python3","/app/recorder.py"]
