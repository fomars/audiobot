import os
import tempfile

import youtube_dl

import celery
import logging

from app.audio_processing import loudnorm, VideoProcessor, get_file_duration_seconds
from app.replies import send_audio, send_video, send_message
from app.models.job import Job
from app.models.user import UserDAL, InsufficientBalanceError
from app.settings import (
    REDIS_HOST,
    REDIS_PORT,
    OUTPUT_DIR,
    BACKEND_DB,
    BROKER_DB,
    INPUT_DIR,
    API_WORKDIR,
)

BROCKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{BROKER_DB}"
BACKEND_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{BACKEND_DB}"

celery_app = celery.Celery(
    "AudioWorker", broker=BROCKER_URL, backend=BACKEND_URL, include=["app", "app.tasks"]
)

logger = logging.getLogger()


@celery_app.task
def process_audio(
    api_fpath: str,
    algorithm: str,
    kwargs,
    chat_id,
    msg_id,
    user_id,
    og_filename,
):
    fpath = api_fpath.replace(API_WORKDIR, INPUT_DIR)
    duration = get_file_duration_seconds(fpath)
    job_id = Job.create(user_id=user_id, file_path=fpath, audio_length=duration)
    success = False
    try:
        UserDAL.deduct_balance(user_id, duration)
        processed_fpath = loudnorm(fpath, OUTPUT_DIR, algorithm, kwargs)
        send_audio(processed_fpath, chat_id, msg_id, og_filename, duration)
        success = True
    except InsufficientBalanceError as e:
        send_message(
            chat_id,
            "Insufficient balance to process the audio.\n"
            f"Your balance: {e.balance} seconds\n"
            f"Audio length: {e.required} seconds",
        )
    except Exception as e:
        logger.error(f"Error processing audio: {e}", exc_info=True)
        UserDAL.top_up_balance(user_id, duration)
        send_message(
            chat_id, "Couldn't process file due to internal error. Please contact the developer."
        )
        Job.mark_completed(job_id, False)
    finally:
        os.remove(fpath)
        Job.mark_completed(job_id, success)


@celery_app.task
def process_video(
    api_fpath: str,
    algorithm: str,
    kwargs: dict,
    chat_id: int,
    msg_id: int,
):
    fpath = api_fpath.replace(API_WORKDIR, INPUT_DIR)
    vp = VideoProcessor(fpath)
    processed_fpath = vp.loudnorm(OUTPUT_DIR, algorithm, kwargs)
    send_video(processed_fpath, chat_id, msg_id, vp.duration, vp.width, vp.height)
    os.remove(fpath)


OPTIONS = {
    "format": "bestaudio",
    "extractaudio": True,  # only keep the audio
    "audioformat": "mp3",  # convert to mp3
    "ext": "mp3",
    "noplaylist": True,  # only download single song, not playlist
}


@celery_app.task
def process_streaming_audio(url):
    with tempfile.TemporaryDirectory() as temp_dir:
        options = dict(OPTIONS, outtmpl=f"{temp_dir}/%(id)s.%(ext)s")
        with youtube_dl.YoutubeDL(options) as dl:
            dl.download([url])
        downloaded_file = os.path.join(temp_dir, os.listdir(temp_dir)[0])
        processed_file = loudnorm(downloaded_file, OUTPUT_DIR, target_loudness=-13)
    return processed_file
