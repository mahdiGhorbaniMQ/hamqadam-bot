# Use official Python base image
FROM python:3.11-slim

# Set work directory inside container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Run the app (adjust this if you have a different entry)
CMD ["python", "-m", "bot.main"]
