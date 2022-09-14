FROM python:3.9-slim
ENV PYTHONUNBUFFERED 1
RUN apt update -y && apt install libpq-dev python3-dev -y
WORKDIR /code
RUN python -m pip install --upgrade pip
RUN pip install --upgrade setuptools
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8080