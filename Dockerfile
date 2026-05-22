FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt setup.py ./
COPY networksecurity ./networksecurity
COPY app ./app
COPY streamlit_app ./streamlit_app
COPY data_schema ./data_schema
COPY final_model ./final_model
COPY Artifacts ./Artifacts
COPY README.md ./README.md

RUN pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
