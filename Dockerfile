FROM python:3.12

RUN wget -nc https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt -y update
RUN  apt install -y ./google-chrome-stable_current_amd64.deb
#COPY ./chromedriver_linux64.zip ./chromedriver_linux64.zip
# install chromedriver
RUN apt-get install -yqq unzip
RUN wget https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.69/linux64/chromedriver-linux64.zip
RUN unzip ./chromedriver-linux64.zip
RUN mv chromedriver-linux64/chromedriver /usr/local/bin/

ENV DISPLAY=:99

WORKDIR /app

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app
