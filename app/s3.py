from urllib.parse import urlparse, urljoin
import boto3
import os
import tempfile

from app.settings import CLOUDCUBE_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

BUCKET = urlparse(CLOUDCUBE_URL).netloc.split('.')[0]
BASE_URL, CUBE = CLOUDCUBE_URL.rsplit('/', 1)


s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


def get_key(fname, public=False):
    return f'{CUBE}/public/audio_output/{fname}' if public else f'{CUBE}/audio_output/{fname}'


def get_link_from_key(key):
    return urljoin(BASE_URL, key)


def upload(fpath, public=False):
    key = get_key(os.path.basename(fpath), public)
    s3.upload_file(
        Filename=fpath,
        Bucket=BUCKET,
        Key=key,
    )
    return key


def download(key):
    dest = os.path.join(tempfile.gettempdir(), key.split('/')[-1])
    s3.download_file(
        Bucket=BUCKET,
        Key=key,
        Filename=dest
    )
    return dest
