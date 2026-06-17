FROM python:3.13

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8003

# Run Flask using Gunicorn for production-ready threading
CMD ["gunicorn", "--bind", "0.0.0.0:8003", "app:app"]