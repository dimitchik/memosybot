from telegram import Update, Chat, ParseMode
from telegram.ext import CallbackContext
import requests
import urllib.request
import os
from media import get_length, loop_video, loop_audio, download_stream_start_dur, download_stream
import settings
from memosybot import error_message

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def coub_parse(update: Update, context: CallbackContext, url: str):
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
            success_video(update, context, file.read(), url)


def ninegag_parse(update: Update, context: CallbackContext, url: str):
    id = url.split('/')[-1]
    if '?' in id:
        id = id.split('?')[0]
    videoUrl = 'https://9gag.com/photo/%s_460sv.mp4' % (id)
    requests.get(videoUrl, headers=headers)
    success_video(update, context, videoUrl, url)


dart_path = os.path.join('.', 'yt_download', 'bin', 'yt_download.dart')
clipDuration = '00:05:00'


def youtube_parse(update: Update, context: CallbackContext, url: str):
    import pytube
    starttime = '0'
    if 't=' in url:
        starttime = url.split('t=')[1].split('&')[0]
    youtubeObject = pytube.YouTube(url)
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
    download_stream_start_dur(streamurl, starttime, '60', videoFile)
    with open(videoFile, 'rb') as file:
        success_video(update, context, file.read(), url)


def reddit_parse(update: Update, context: CallbackContext, url: str):
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
        success_video(update, context, file.read(), url)


def success_video(update: Update, context: CallbackContext, video: str | bytes, url: str):
    if update.effective_chat is not None:
        message = context.bot.send_video(
            chat_id=update.effective_chat.id, video=video)
        if update.effective_chat.type != Chat.PRIVATE:
            context.bot.edit_message_caption(
                chat_id=update.effective_chat.id, message_id=message.message_id,
                caption='<a href="tg://user?id=%s">%s</a>\n%s' % (
                    update.message.from_user.id, update.message.from_user.full_name,
                    update.message.text
                ),
                parse_mode=ParseMode.HTML
            )
            if update.message.parse_entity(update.message.entities[-1]) == url:
                context.bot.delete_message(
                    chat_id=update.effective_chat.id, message_id=update.message.message_id
                )
    else:
        context.bot.send_message(
            chat_id=settings.debug_chat_id, text="WTF: %s\n%s\n%s" % (url, update, context))
        context.bot.send_video(
            chat_id=settings.debug_chat_id, video=video, reply_to_message_id=update.message.message_id)
