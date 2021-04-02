FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m pip install --upgrade pip
RUN pip3 install -U pip setuptools wheel

# youtube-dl install
RUN wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl
RUN chmod a+rx /usr/local/bin/youtube-dl

COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

# install opus and ffmpeg
RUN apt update
RUN apt install libopus0
RUN apt install ffmpeg -y

RUN mkdir /discord-bot
COPY ./src/ discord-bot/src/

WORKDIR /discord-bot
COPY ./scripts/ .
RUN chmod +x ./*.sh

CMD ["./entrypoint.sh"]
