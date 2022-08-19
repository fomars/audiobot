import re
import os
import ffmpeg
import logging

from sys import argv
from decimal import getcontext, Decimal

from app.commands import MainCommands
from app.settings import app_settings

logger = logging.getLogger()

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
    for stream in probe["streams"]:
        if stream.get("codec_type") == "audio":
            return int(stream.get("bit_rate", 192000))
    else:
        return 192000


def loudnorm(file_path: str, output_dir: str, algorithm, kwargs):
    assert os.path.exists(file_path)

    fname, ext = os.path.splitext(os.path.basename(file_path))
    output_path = os.path.join(output_dir, f"{fname}_out.mp3")
    bitrate = min(get_audio_bitrate(file_path), 256000)

    inp = ffmpeg.input(file_path)
    prepared_cmd = algorithms.get(algorithm, AudioProcessor.default_loudnorm)(inp, **kwargs).output(
        output_path, ar=44100, format="mp3", audio_bitrate=bitrate
    )

    logger.info(f"ffmpeg cmd:\n{' '.join(prepared_cmd.compile())}")
    prepared_cmd.run(overwrite_output=True)
    return output_path


class AudioProcessor:
    @staticmethod
    def default_loudnorm(ffmpeg_inp, loudness=app_settings.default_loudness, **kw):
        return ffmpeg_inp.audio.filter("loudnorm", i=loudness, tp=-0.7)

    @staticmethod
    def enhance_speech(ffmpeg_inp, **kw):
        return (
            ffmpeg_inp.audio.filter("highpass", f=150)
            .filter("asubcut", cutoff=80)
            .filter("lowpass", f=12500)
            .filter("loudnorm", i=-18, tp=-0.7)
        )

    @staticmethod
    def small_speakers(
        ffmpeg_inp,
        loudness=app_settings.default_loudness,
        low_cut=app_settings.default_low_cut,
        **kw,
    ):
        low_cut = min(max(int(low_cut), app_settings.min_low_cut), app_settings.max_low_cut)
        return ffmpeg_inp.audio.filter("asubcut", cutoff=low_cut).filter(
            "loudnorm", i=loudness, tp=-0.7
        )


algorithms = {
    MainCommands.make_it_loud.value: AudioProcessor.default_loudnorm,
    MainCommands.enhance_speech.value: AudioProcessor.enhance_speech,
    MainCommands.small_speakers.value: AudioProcessor.small_speakers,
}


class VideoProcessor:
    def __init__(self, filepath):
        assert os.path.exists(filepath)
        self.file_path = filepath
        self.probe = ffmpeg.probe(filepath)
        self.duration = self.probe["format"]["duration"]
        self.width, self.height = self.__get_resolution()

        for stream in self.probe["streams"]:
            if stream.get("codec_type") == "audio":
                self.audio_bitrate = min(int(stream.get("bit_rate", 192000)), 192000)
            elif stream.get("codec_type") == "video":
                self.video_bitrate = stream.get("bit_rate")

    def __get_resolution(self) -> (int, int):
        for stream in self.probe["streams"]:
            if stream.get("codec_type") == "video":
                if (
                    stream.get("side_data_list")
                    and stream["side_data_list"][0].get("rotation", 0) % 180
                ):
                    return stream.get("height"), stream.get("width")
                else:
                    return stream.get("width"), stream.get("height")

    def loudnorm(self, output_dir: str, algorithm, kwargs):
        fname, ext = os.path.splitext(os.path.basename(self.file_path))
        output_path = os.path.join(output_dir, f"{fname}_out.mp4")

        inp = ffmpeg.input(self.file_path)
        audio_norm = algorithms[algorithm](inp, **kwargs)

        prepared_cmd = ffmpeg.output(
            inp.video,
            audio_norm,
            output_path,
            format="mp4",
            ar=44100,
            audio_bitrate=self.audio_bitrate,
            video_bitrate=self.video_bitrate,
        )

        logger.info(f"ffmpeg cmd:\n{' '.join(prepared_cmd.compile())}")
        prepared_cmd.run(overwrite_output=True)

        return output_path


if __name__ == "__main__":
    input_fpath = argv[1]
    assert os.path.exists(input_fpath)

    fname, ext = os.path.splitext(os.path.basename(input_fpath))
    output_path = os.path.join(OUTPUT, fname + ".mp3")

    out = (
        ffmpeg.input(input_fpath)
        .filter("loudnorm", i=-14, tp=-0.7)
        .output(output_path, ar=44100, format="mp3", audio_bitrate="256k")
        .run(overwrite_output=True)
    )

    print(output_path)
