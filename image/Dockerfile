FROM python:3.8

WORKDIR /image

EXPOSE 8080

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app/ ./app

ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

