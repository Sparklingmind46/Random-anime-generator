# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy project files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for health checks
EXPOSE 8080

# Run both the bot and health check
CMD ["sh", "-c", "python bot.py & python health_check.py"]
