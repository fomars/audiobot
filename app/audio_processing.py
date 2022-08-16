import re
from typing import Union

import ffmpeg
from sys import argv
import os
from decimal import getcontext, Decimal

getcontext().prec = 2


OUTPUT = "samples/output"
NORMALIZE_CMD = (
    "ffmpeg-normalize samples/input/djset.mp3 -of samples/output/ -ext mp3 -c:a mp3"
    " -b:a 256000 -f -nt peak -t -0.3"
)


def get_max_vol(file_path: str):
    stdout, stderr = (
        ffmpeg.input(file_path)
        .filter("volumedetect")
        .output("/dev/null", format="null")
        .run(capture_stderr=True)
    )
    for line in stderr.decode().split("\n"):
        if "max_volume:" in line:
            max_vol_str = line
    return Decimal(re.match(r".+max_volume:\s(.+?)\s", max_vol_str).groups()[0])


def get_audio_bitrate(filename):
    probe = ffmpeg.probe(filename)
    try:
        for stream in probe["streams"]:
            if stream["codec_type"] == "audio":
                return int(stream["bit_rate"])
    finally:
        return 192000


def get_resolution(filename) -> (int, int):
    probe = ffmpeg.probe(filename)
    try:
        return probe["streams"][0]["width"], probe["streams"][0]["height"]
    except KeyError:
        return None, None


def loudnorm(file_path: str, output_dir: str, target_loudness: Union[int, str]):
    assert os.path.exists(file_path)

    fname, ext = os.path.splitext(os.path.basename(file_path))
    output_path = os.path.join(output_dir, f"{fname}_out.mp3")
    bitrate = min(get_audio_bitrate(file_path), 256000)

    ffmpeg.input(file_path).filter("loudnorm", i=target_loudness, tp=-0.1).output(
        output_path, ar=44100, format="mp3", audio_bitrate=bitrate
    ).run(overwrite_output=True)

    return output_path


def loudnorm_video(file_path: str, output_dir: str, target_loudness: Union[int, str]):
    assert os.path.exists(file_path)

    fname, ext = os.path.splitext(os.path.basename(file_path))
    output_path = os.path.join(output_dir, f"{fname}_out.mp4")
    bitrate = min(get_audio_bitrate(file_path), 192000)

    inp = ffmpeg.input(file_path)
    audio_norm = inp.audio.filter("loudnorm", i=target_loudness, tp=-0.1)
    ffmpeg.output(
        inp.video, audio_norm, output_path, format="mp4", ar=44100, audio_bitrate=bitrate
    ).run(overwrite_output=True)

    return output_path


if __name__ == "__main__":
    input_fpath = argv[1]
    assert os.path.exists(input_fpath)

    fname, ext = os.path.splitext(os.path.basename(input_fpath))
    output_path = os.path.join(OUTPUT, fname + ".mp3")

    out = (
        ffmpeg.input(input_fpath)
        .filter("loudnorm", i=-14, tp=-0.1)
        .output(output_path, ar=44100, format="mp3", audio_bitrate="256k")
        .run(overwrite_output=True)
    )

    print(output_path)
