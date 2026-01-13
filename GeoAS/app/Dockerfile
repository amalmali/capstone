FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libportaudio2 \
    portaudio19-dev \
    libasound2-dev \
    libsndfile1 \
  && rm -rf /var/lib/apt/lists/*

# Copy and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]