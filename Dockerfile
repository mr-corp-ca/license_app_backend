# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt to the container
COPY requirements.txt /app/

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the container
COPY . /app/

# Expose the port Django will run on (default is 8000)
EXPOSE 8400

# Run migrations and start the Django server
CMD ["python", "manage.py", "migrate"]  # This will run migrations
CMD ["python", "manage.py", "runserver", "0.0.0.0:8400"]  # Run the Django server
