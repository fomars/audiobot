import os
import tempfile
from urllib.request import urlretrieve

import youtube_dl

from app.audio_processing import loudnorm
from app.s3 import upload
from app.settings import BROKER_URL
import logging
import celery

app = celery.Celery(
    'AudioWorker',
    backend=BROKER_URL,
    broker=BROKER_URL,
    include=['app', 'app.tasks']
)


logger = logging.getLogger()


@app.task
def make_it_loud(audio_url, fname):
    logger.debug(f'audio_url: {audio_url}')
    fpath = os.path.join(tempfile.gettempdir(), fname)
    urlretrieve(audio_url, fpath)
    processed_fpath = loudnorm(fpath)
    os.remove(fpath)
    processed_s3_key = upload(processed_fpath)
    os.remove(processed_fpath)
    return processed_s3_key


OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,  # only keep the audio
    'audioformat': "mp3",  # convert to mp3
    'ext': "mp3",
    'noplaylist': True,    # only download single song, not playlist
}


@app.task
def process_streaming_audio(url, title):
    with tempfile.TemporaryDirectory() as temp_dir:
        options = dict(OPTIONS, outtmpl=f'{temp_dir}/%(id)s.%(ext)s')
        with youtube_dl.YoutubeDL(options) as dl:
            dl.download([url])
        downloaded_file = os.path.join(
            temp_dir, os.listdir(temp_dir)[0]
        )
        processed_file = loudnorm(downloaded_file)
    processed_s3_key = upload(processed_file, public=True)
    os.remove(processed_file)
    return processed_s3_key
