FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install pip
RUN pip install --upgrade pip

# Install dependencies individually
RUN pip install python-telegram-bot==13.5
RUN pip install yt-dlp==2025.1.12
RUN pip install requests
RUN pip install psycopg2
RUN pip install pyTelegramBotAPI
RUN pip install python-dotenv
RUN pip install Flask==2.2.5
RUN pip install gunicorn==22.0.0

# Expose the port
EXPOSE 80

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
