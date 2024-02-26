FROM python:3.12

RUN wget -nc https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt update -y
RUN apt install -y ./google-chrome-stable_current_amd64.deb

ENV DISPLAY=:99

WORKDIR /app

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app
