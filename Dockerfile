FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Устанавливаем PYTHONPATH, чтобы Python видел папку src
ENV PYTHONPATH=/app

# Запускаем main.py из корня
CMD ["python", "src/main.py"]