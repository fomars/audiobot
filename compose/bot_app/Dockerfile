FROM python:3.9-slim as bot-base

COPY requirements.txt ./
COPY ./app /app
COPY ./main.py /

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="."
ARG DEBIAN_FRONTEND=noninteractive

RUN     apt-get -yqq update && \
        apt-get install -yqq --no-install-recommends ca-certificates ffmpeg

RUN pip install --no-cache-dir -r requirements.txt

FROM bot-base

CMD [ "python", "main.py" ]