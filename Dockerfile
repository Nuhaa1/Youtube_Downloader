# Use a Python base image
FROM python:3.9-slim

# Install ffmpeg and supervisor
RUN apt-get update && apt-get install -y \
    ffmpeg \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (the same port used in Gunicorn)
EXPOSE 5000

# Create supervisord.conf on the fly
RUN echo "[supervisord]\nnodaemon=true\n\n[program:flask]\ncommand=/app/entrypoint.sh\nautostart=true\nautorestart=true\n\n[program:yt]\ncommand=python /app/yt.py\nautostart=true\nautorestart=true" > /etc/supervisor/conf.d/supervisord.conf

# Create entry script
RUN echo '#!/bin/sh\nexec gunicorn server:app --bind 0.0.0.0:$PORT' > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Use supervisor to manage processes
CMD ["/usr/bin/supervisord"]
