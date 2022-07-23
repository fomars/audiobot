import os
import tempfile
from typing import Union
from urllib.parse import urljoin

import youtube_dl

import celery
import logging

from app.audio_processing import loudnorm
from app.settings import REDIS_HOST, REDIS_PORT, OUTPUT_DIR, BACKEND_DB, BROKER_DB

BROCKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{BROKER_DB}"
BACKEND_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{BACKEND_DB}"

app = celery.Celery(
    'AudioWorker',
    broker=BROCKER_URL,
    backend=BACKEND_URL,
    include=['app', 'app.tasks']
)


logger = logging.getLogger()


@app.task
def make_it_loud(file_path: str, target_loudness: Union[int, str]):
    processed_fpath = loudnorm(file_path, OUTPUT_DIR, target_loudness)
    return processed_fpath


OPTIONS = {
    'format': 'bestaudio',
    'extractaudio': True,  # only keep the audio
    'audioformat': "mp3",  # convert to mp3
    'ext': "mp3",
    'noplaylist': True,    # only download single song, not playlist
}


@app.task
def process_streaming_audio(url):
    with tempfile.TemporaryDirectory() as temp_dir:
        options = dict(OPTIONS, outtmpl=f'{temp_dir}/%(id)s.%(ext)s')
        with youtube_dl.YoutubeDL(options) as dl:
            dl.download([url])
        downloaded_file = os.path.join(
            temp_dir, os.listdir(temp_dir)[0]
        )
        processed_file = loudnorm(downloaded_file, OUTPUT_DIR, target_loudness=-13)
    return processed_file
