# syntax=docker/dockerfile:1

FROM python:3.9-slim

WORKDIR /app

COPY ./requirements.txt .
RUN apt-get update -y
RUN apt-get install locales locales-all -y
RUN apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info -y
RUN pip3 install -r requirements.txt

CMD ["/bin/bash", "./start.sh"]
