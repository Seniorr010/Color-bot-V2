# Python'un yüngül versiyasını istifadə edirik
FROM python:3.11-slim

# İş qovluğunu təyin edirik
WORKDIR /app

# Lazımi sistem paketlərini quraşdırırıq (əgər lazım olsa)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Dependency-ləri kopyalayırıq və quraşdırırıq
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Botun kodlarını kopyalayırıq
COPY . .

# Botu işə salırıq
CMD ["python", "bot.py"]
