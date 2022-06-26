import urllib
import boto3
from settings import CLOUDCUBE_URL
import os
import tempfile

BUCKET = urllib.parse.urlparse(CLOUDCUBE_URL).netloc.split('.')[0]
CUBE = CLOUDCUBE_URL.split('/')[-1]

s3 = boto3.client("s3")


def get_key(fname):
    return f'{CUBE}/audio_output/{fname}'


def upload(fpath):
    key = get_key(os.path.basename(fpath))
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
