# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput
# Expose port 8000 for Django app
EXPOSE 8000


# Add a wait script to ensure Postgres is up before starting Django
COPY ./wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Define environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Run migrations and start the ASGI server using Daphne
CMD ["./wait-for-it.sh", "db:5432", "--", "daphne", "-b", "0.0.0.0", "-p", "8000", "momentus.asgi:application"]
