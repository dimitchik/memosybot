import subprocess
from pymediainfo import MediaInfo


def get_length(input: str) -> int:
    media_info = MediaInfo.parse(input)
    duration_in_ms = media_info.tracks[0].duration  # type: ignore
    return duration_in_ms


def loop_video(video: str, audio: str, result: str):
    subprocess.run(['ffmpeg',  '-stream_loop', '-1', '-i', video, '-i', audio, '-shortest',
                   '-map', '0:v:0', '-map', '1:a:0', '-y', """%s""" % result], encoding='utf-8-sig')


def loop_audio(video: str, audio: str, result: str):
    subprocess.run(['ffmpeg', '-i', video, '-stream_loop', '-1', '-i', audio, '-shortest',
                   '-map', '0:v:0', '-map', '1:a:0', '-y', """%s""" % result], encoding='utf-8-sig')


def cut_video(video: str, start: str, end: str, result: str):
    subprocess.run(['ffmpeg', '-i', video, '-ss', start,
                   '-t', end, '-async', '1', '-y', result], encoding='utf-8-sig')


def download_stream(url: str, start: str, end: str, result: str):
    subprocess.run(['ffmpeg', '-i', url, '-ss', start,
                   '-t', end, '-c', 'copy', '-y', result], encoding='utf-8-sig')
