import re
import tempfile

import ffmpeg
from sys import argv
import os
from decimal import *

import settings

getcontext().prec = 2


OUTPUT = 'samples/output'
NORMALIZE_CMD =\
    'ffmpeg-normalize samples/input/djset.mp3 -of samples/output/ -ext mp3 -c:a mp3 -b:a 256000 -f -nt peak -t -0.3'


def get_max_vol(file_path: str):
    stdout, stderr = ffmpeg.\
        input(file_path).\
        filter('volumedetect').\
        output('/dev/null', format='null').\
        run(capture_stderr=True)
    for line in stderr.decode().split('\n'):
        if 'max_volume:' in line:
            max_vol_str = line
    return Decimal(re.match(r'.+max_volume:\s(.+?)\s', max_vol_str).groups()[0])


def get_bitrate(filename):
    probe = ffmpeg.probe(filename)
    try:
        return int(probe['streams'][0]['bit_rate'])
    except (IndexError, KeyError):
        return 128000


def loudnorm(file_path):
    assert os.path.exists(file_path)

    fname, ext = os.path.splitext(os.path.basename(file_path))
    output_path = os.path.join(tempfile.gettempdir(), f'{fname}_out.mp3')
    bitrate = min(get_bitrate(file_path), 256000)

    out = ffmpeg. \
        input(file_path). \
        filter("loudnorm", i=settings.TARGET_LOUDNESS, tp=-0.1). \
        output(output_path, ar=44100, format='mp3', audio_bitrate=bitrate). \
        run(overwrite_output=True)

    return output_path


if __name__ == "__main__":
    input_fpath = argv[1]
    assert os.path.exists(input_fpath)

    fname, ext = os.path.splitext(os.path.basename(input_fpath))
    output_path = os.path.join(OUTPUT, fname+'.mp3')

    out = ffmpeg.\
        input(input_fpath).\
        filter("loudnorm", i=-14, tp=-0.1).\
        output(output_path, ar=44100, format='mp3', audio_bitrate='256k').\
        run(overwrite_output=True)

    print(output_path)