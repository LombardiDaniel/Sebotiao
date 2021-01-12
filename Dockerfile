FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m pip install --upgrade pip
RUN pip3 install -U pip setuptools wheel

COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

RUN mkdir /discord-bot
COPY ./src/ discord-bot/src/

WORKDIR /discord-bot
COPY ./scripts/ .
RUN chmod +x ./*.sh

CMD ["./entrypoint.sh"]
