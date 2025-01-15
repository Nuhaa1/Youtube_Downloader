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

# Expose the port
EXPOSE 5000

# Copy supervisord.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Use supervisor to manage processes
CMD ["/usr/bin/supervisord"]
