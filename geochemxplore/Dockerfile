FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make run script executable
COPY run.sh .
RUN chmod +x run.sh

CMD ["./run.sh"]