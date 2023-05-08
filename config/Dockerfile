# syntax=docker/dockerfile:1
FROM python:3.9-slim

WORKDIR /app

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

CMD ["/bin/bash", "./start.sh"]