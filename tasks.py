import os
import tempfile
import uuid
from urllib.request import urlretrieve

import youtube_dl

from audio_processing import loudnorm
import logging
import celery
from s3 import upload

app = celery.Celery('AudioWorker')
app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])


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
    unique_name = str(uuid.uuid4())[-10:]
    options = dict(OPTIONS, outtmpl=f'{unique_name}.%(ext)s')
    filename = f"{unique_name}.{options['ext']}"
    with youtube_dl.YoutubeDL(options) as dl:
        dl.download([url])
    processed_fpath = loudnorm(filename)
    os.remove(filename)
    processed_s3_key = upload(processed_fpath, public=True)
    os.remove(processed_fpath)
    return processed_s3_key
