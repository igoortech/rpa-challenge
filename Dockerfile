FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV OUTPUT_DIR=/app/output
RUN mkdir -p /app/output

CMD ["python", "main.py"]
