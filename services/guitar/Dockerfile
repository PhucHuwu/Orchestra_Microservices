FROM python:3.11-slim

WORKDIR /app

COPY services/guitar/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/__init__.py ./services/__init__.py
COPY services/instruments_shared ./services/instruments_shared
COPY services/guitar/app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
