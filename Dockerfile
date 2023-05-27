# syntax=docker/dockerfile:1
FROM ubuntu:latest
WORKDIR /app
COPY requirements.txt requirements.txt
RUN set -xe \
    && apt-get update -y \
    && apt-get install -y python3-pip
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
COPY main.py main.py
CMD ["uvicorn", "main:app" , "--port=9988", "--reload"]