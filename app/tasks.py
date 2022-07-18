import os
import tempfile
from urllib.request import urlretrieve

import youtube_dl

import celery
import logging

from app.audio_processing import loudnorm
from app.files import BotFile
from app.settings import BROKER_URL, OUTPUT_DIR

app = celery.Celery(
    'AudioWorker',
    backend=BROKER_URL,
    broker=BROKER_URL,
    include=['app', 'app.tasks']
)


logger = logging.getLogger()


@app.task
def make_it_loud(file_path: str):
    processed_fpath = loudnorm(file_path, OUTPUT_DIR)
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
        processed_file = loudnorm(downloaded_file, OUTPUT_DIR)
    return processed_file
