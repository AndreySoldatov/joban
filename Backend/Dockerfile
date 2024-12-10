FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install sqlite3 
COPY app ./app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD [ "fastapi", "run", "app/main.py" ]