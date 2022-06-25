import os
import tempfile
from urllib.request import urlretrieve
from audio_processing import loudnorm
import logging
import celery

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
    return processed_fpath
