# syntax=docker/dockerfile:1

FROM python:3.9.7-slim-bullseye 
WORKDIR /usr/src/app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# system dependencies
ENV NODE_VERSION=16.8.0
RUN apt-get update
RUN apt install -y curl git gcc python3-dev
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"

# python dependencies
COPY ./requirements.txt .
COPY . .
RUN pip install -r requirements.txt
RUN npm i -g nodemon

# CMD ["nodemon", "--exec", "python", "main.py"]
