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

# ffmpeg install
RUN wget https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-armhf-static.tar.xz
RUN tar -xf ffmpeg-git-armhf-static.tar.xz
RUN mv ffmpeg-git-20210325-armhf-static/ffmpeg /usr/bin/ffmpeg

# opus install
RUN apt-get update
RUN apt-get install libopus0

RUN mkdir /discord-bot
COPY ./src/ discord-bot/src/

WORKDIR /discord-bot
COPY ./scripts/ .
RUN chmod +x ./*.sh

CMD ["./entrypoint.sh"]
