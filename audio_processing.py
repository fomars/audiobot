import re

import ffmpeg
from sys import argv
import os
from decimal import *

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


def get_codec_name(probe: dict) -> str:
    return probe['streams'][0]['codec_name']


if __name__ == "__main__":
    input_fpath = argv[1]
    assert os.path.exists(input_fpath)

    fname = os.path.basename(input_fpath)
    output_path = os.path.join(OUTPUT, fname)

    out = ffmpeg.\
        input(input_fpath).\
        filter("loudnorm", i=-14, tp=-0.1).\
        output(output_path, ar=44100, audio_bitrate='320k').\
        run(overwrite_output=True)

    print(output_path)