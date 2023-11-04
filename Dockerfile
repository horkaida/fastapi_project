FROM python:3.11.6-alpine3.18

WORKDIR /app
EXPOSE 8000

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
