# 1️⃣ Base image
FROM python:3.11-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4️⃣ Install system dependencies (خفيفة)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5️⃣ Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 6️⃣ Copy project files
COPY . .

# 7️⃣ Default command
CMD ["python", "app/main.py"]
