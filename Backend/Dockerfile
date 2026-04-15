FROM python:3.12
WORKDIR /app
COPY requirements.lock.txt .
RUN pip install --no-cache-dir -r requirements.lock.txt
RUN apt-get update && apt-get install -y --no-install-recommends sqlite3 && rm -rf /var/lib/apt/lists/*
COPY app ./app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD [ "fastapi", "run", "app/main.py" ]