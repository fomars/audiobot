FROM python:3.9-slim as bot-base

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="."
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -yqq update && \
    apt-get install -yqq --no-install-recommends ca-certificates wget xz-utils && \
    apt-get clean

RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar -xvf *.tar.xz && \
    rm -f *.tar.xz && \
    mv ./ffmpeg-*/ffmpeg /usr/bin/ffmpeg && \
    mv ./ffmpeg-*/ffprobe /usr/bin/ffprobe

COPY requirements.txt ./

RUN pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt

FROM bot-base

COPY ./app /app
COPY ./alembic /alembic
COPY ./main.py ./alembic.ini /

CMD [ "python", "main.py" ]