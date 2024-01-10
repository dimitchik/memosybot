
from telegram import Update, Chat, constants
from telegram.ext import CallbackContext, ContextTypes
import requests
import urllib.request
import os
from media import get_length, loop_video, loop_audio, download_stream_start_dur, download_stream
import settings
from memosybot import error_message

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


async def coub_parse(update: Update, context: CallbackContext, url: str):
    id = url.split('/')[-1]
    requestUrl = 'https://coub.com/api/v2/coubs/%s' % (id)
    response = requests.get(requestUrl, headers=headers)
    if response._content is not None:
        response.raise_for_status()
        params = response.json()
        videoUrl = params['file_versions']['mobile']['video']
        videoFile = urllib.request.urlretrieve(
            videoUrl)[0]
        videoFile = os.path.abspath(videoFile)
        audioUrl = params['file_versions']['mobile']['audio'][0]
        audioFile = urllib.request.urlretrieve(
            audioUrl)[0]
        audioFile = os.path.abspath(audioFile)
        videoLength = get_length(videoFile)
        audioLength = get_length(audioFile)
        result = '%s_merged.mp4' % videoUrl.split(
            '/')[-1].split('.')[0]
        result = os.path.abspath(result)
        if audioLength > videoLength:
            loop_video(videoFile, audioFile, result)
        else:
            loop_audio(videoFile, audioFile, result)
        with open(result, 'rb') as file:
            await success_video(update, context, file.read(), url)


def ninegag_parse(update: Update, context: CallbackContext, url: str):
    id = url.split('/')[-1]
    if '?' in id:
        id = id.split('?')[0]
    videoUrl = 'https://9gag.com/photo/%s_460sv.mp4' % (id)
    requests.get(videoUrl, headers=headers)
    return success_video(update, context, videoUrl, url)


dart_path = os.path.join('.', 'yt_download', 'bin', 'yt_download.dart')
clipDuration = '00:05:00'


def youtube_parse_old(update: Update, context: CallbackContext, url: str, dur: str = '60', orig_url: str | None = None):
    from pytube import YouTube
    if orig_url is None:
        orig_url = url
    starttime = '0'
    if 't=' in url:
        starttime = url.split('t=')[1].split('&')[0]
    youtubeObject = YouTube(url)
    stream = youtubeObject.streams.get_by_resolution('360p')
    if stream is None:
        stream = youtubeObject.streams.get_by_resolution('240p')
    if stream is None:
        stream = youtubeObject.streams.get_by_resolution('144p')
    if stream is None:
        error_message('Could not find any resolution',
                      update=update, context=context)
        return
    streamurl = stream.url
    videoFile = '%s.mp4' % youtubeObject.video_id
    print(streamurl)
    download_stream_start_dur(streamurl, starttime, dur, videoFile)
    with open(videoFile, 'rb') as file:
        success_video(update, context, file.read(), orig_url)

final_filename = None

def yt_dlp_monitor(d):
    global final_filename
    final_filename  = d.get('info_dict').get('_filename')

def youtube_parse(update: Update, context: CallbackContext, url: str):
    from yt_dlp import YoutubeDL
    timestamp = int(url.split('t=')[1].split('&')[0])
    if not timestamp:
        timestamp = 0
    ranges = lambda _, __ : [{'start_time': timestamp, 'end_time': timestamp+300}]
    with YoutubeDL({
        'outtmpl': {'default': '%(id)s.%(ext)s'},
        'format': '(b[fps>30]/b)[height<=720][ext=mp4]/(w[fps>30][ext=mp4]/w[ext=mp4]/w)',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'prefer_ffmpeg': True,
        "progress_hooks": [yt_dlp_monitor],
        'max_filesize': 100000000,
        'download_ranges': ranges
    }) as ydl:
        ydl.download([url])
    global final_filename
    if not os.path.exists(final_filename):
        for root, dirs, files in os.walk('./'):
            for file in files:
                if final_filename.split('.')[0] in file and file.endswith('.mp4'):
                    final_filename = file

    return success_video(update, context, final_filename, url)

def youtube_clip_parse(update: Update, context: CallbackContext, url: str):
    from bs4 import BeautifulSoup, Tag, NavigableString
    import re
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    video_url = soup.find('meta', property='og:video:url')
    if isinstance(video_url, Tag):
        video_url = video_url.attrs['content']
    elif isinstance(video_url, NavigableString):
        video_url = video_url[0].split('content="')[1].split('"')[0]
    else:
        video_url = url
    video_id = video_url.split('/')[-1].split('?')[0]
    video_url = 'https://www.youtube.com/watch?v=%s' % video_id
    pattern = r"\"?startTimeMs\"? *: *\"(\d+)\""
    matches = re.findall(pattern, response.text)
    start_time = matches.pop()
    start_time = int(start_time) // 1000
    pattern = r"\"?endTimeMs\"? *: *\"(\d+)\""
    matches = re.findall(pattern, response.text)
    end_time = matches.pop()
    end_time = int(end_time) // 1000
    dur = end_time - start_time
    if dur > 60:
        dur = 60
    dur = str(dur)
    start_time = str(start_time)
    video_url = '%s&t=%s' % (video_url, start_time)
    youtube_parse(update, context, video_url, dur, url)


async def tiktok_parse(update: Update, context: CallbackContext, url: str):
    import bs4
    ses = requests.Session()
    server_url = 'https://musicaldown.com/'
    headers = {
        "Host": "musicaldown.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "TE": "trailers"
    }
    ses.headers.update(headers)
    req = ses.get(server_url)
    data = {}
    parse = bs4.BeautifulSoup(req.text, 'html.parser')
    get_all_input = parse.findAll('input')
    for i in get_all_input:
        if i.get("id") == "link_url":
            data[i.get("name")] = url
        else:
            data[i.get("name")] = i.get("value")
    post_url = server_url + "id/download"
    req_post = ses.post(post_url, data=data, allow_redirects=True)
    if req_post.status_code == 302 or 'This video is currently not available' in req_post.text or 'Video is private or removed!' in req_post.text:
        error_message('Video private or removed',
                      update=update, context=context)
    elif 'Submitted Url is Invalid, Try Again' in req_post.text:
        error_message('Invalid url',
                      update=update, context=context)
    get_all_blank = bs4.BeautifulSoup(req_post.text, 'html.parser').findAll(
        'a', attrs={'target': '_blank'})
    download_link = get_all_blank[0].get('href')
    videoFile = 'tiktok_%s.mp4' % url.split('/')[-1].split('?')[0]
    download_stream(download_link, videoFile)
    with open(videoFile, 'rb') as file:
        await success_video(update, context, file.read(), url)


async def reddit_parse(update: Update, context: CallbackContext, url: str):
    videoUrl: str
    if 'reddit.com' in url:
        lastslash = url.rfind('/')
        url = url[:lastslash]
        response = requests.get('%s.json' % url, headers=headers)
        response.raise_for_status()
        data = response.json()
        videoUrl = data[0]['data']['children'][0]['data']['secure_media']['reddit_video']['dash_url']
    elif 'v.redd.it' in url:
        videoUrl = '%s/DASHPlaylist.mpd' % url
    else:
        error_message(update=update, context=context)
        return
    videoFile = '%s.mp4' % url.split('/')[-1]
    download_stream(videoUrl, videoFile)
    with open(videoFile, 'rb') as file:
        await success_video(update, context, file.read(), url)


async def success_video(update: Update, context: ContextTypes.DEFAULT_TYPE, video: str | bytes, url: str):
    if update.effective_chat is not None:
        message = await context.bot.send_video(
            chat_id=update.effective_chat.id, video=video)
        if update.effective_chat.type != Chat.PRIVATE:
            await context.bot.edit_message_caption(
                chat_id=update.effective_chat.id, message_id=message.message_id,
                caption='<a href="tg://user?id=%s">%s</a>\n%s' % (
                    update.message.from_user.id, update.message.from_user.full_name,
                    update.message.text
                ),
                parse_mode='HTML'
            )
            if update.message.parse_entity(update.message.entities[-1]) == url:
                await update.message.delete()
    else:
        await context.bot.send_message(
            chat_id=settings.debug_chat_id, text="WTF: %s\n%s\n%s" % (url, update, context))
        await context.bot.send_video(
            chat_id=settings.debug_chat_id, video=video, reply_to_message_id=update.message.message_id)
    if isinstance(video, str) and os.path.exists(video) and not video.startswith('http'):
        os.remove(video)
