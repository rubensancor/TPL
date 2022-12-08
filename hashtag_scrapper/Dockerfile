FROM ubuntu:18.04

RUN apt-get update && apt-get install -y --allow-unauthenticated \
    build-essential \
    python3-dev \
    python3-pip \
    unzip xvfb libxi6 libgconf-2-4 \
    default-jdk curl 

RUN pip3 install --upgrade pip

# Install chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
RUN echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
RUN apt-get -y update
RUN apt-get -y install google-chrome-stable

# Chrome driver
RUN wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver
RUN rm chromedriver_linux64.zip
