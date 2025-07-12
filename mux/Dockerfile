FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY pplx_mux.py .
CMD ["uvicorn", "pplx_mux:aplikacja", "--host", "0.0.0.0", "--port", "8000"]
