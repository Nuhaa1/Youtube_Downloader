# Use a Python base image
FROM python:3.9-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (the same port used in Gunicorn)
EXPOSE 5000

# Create entry script
RUN echo '#!/bin/sh\nexec gunicorn server:app --bind 0.0.0.0:$PORT' > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use the entry script to start the app
ENTRYPOINT ["/app/entrypoint.sh"]
