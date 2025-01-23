FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade yt-dlp

EXPOSE 5000  # Ensure the exposed port matches the one in your Flask app

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "yt:app"]
