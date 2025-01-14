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

# Ensure the virtual environment is activated
ENV PATH="/opt/venv/bin:$PATH"

# Command to run the app
CMD ["python", "app.py"]
