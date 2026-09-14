FROM python:3.12-slim

WORKDIR /code

ENV PYTHONPATH=/code

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

