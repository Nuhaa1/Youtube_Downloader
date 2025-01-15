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

# Set environment variable for port
ENV PORT=5000

# Create supervisord.conf on the fly
RUN echo "[supervisord]\nnodaemon=true\n\n[program:web]\ncommand=python /app/Server.py\nautostart=true\nautorestart=true\n\n[program:worker]\ncommand=python /app/yt.py\nautostart=true\nautorestart=true" > /etc/supervisor/conf.d/supervisord.conf

# Use supervisor to manage processes
CMD ["/usr/bin/supervisord"]
