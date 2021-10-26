# syntax=docker/dockerfile:1

FROM nikolaik/python-nodejs:python3.9-nodejs16
WORKDIR /usr/src/app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# system dependencies
RUN apt-get update
RUN apt-get install git -y

# python dependencies
COPY ./requirements.txt .
COPY . .
RUN pip install -r requirements.txt
RUN npm i -g nodemon

CMD ["nodemon", "--exec", "python", "main.py"]
# CMD ["python", "-m" "watchmedo", "shell-command", '--patterns-"*.py"', '--command="python \"${watch_src_path}\""']