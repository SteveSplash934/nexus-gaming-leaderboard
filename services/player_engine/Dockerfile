FROM python:3.13

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the data directory for the SQLite volume
RUN mkdir -p /app/data

COPY . .

EXPOSE 8001

# Run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]