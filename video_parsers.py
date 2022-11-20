import subprocess
from telegram import Update, Chat, ParseMode
from telegram.ext import CallbackContext
import requests
import urllib.request
import os
import datetime
from media import get_length, loop_video, loop_audio, cut_video
from memosybot import dima_chat_id

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
    id = url
    if 'youtube.com' in url and 'watch?v=' in url:
        id = url.split('watch?v=')[1].split('&')[0]
    if 'youtu.be' in url or 'shorts' in url:
        id = url.split('/')[-1]
        if '?' in id:
            id.split('?')[0]
    print(dart_path)
    result = subprocess.run(['dart', 'run', dart_path, id, ],
                            encoding='utf-8-sig',
                            capture_output=True,
                            text=True,
                            shell=True
                            )
    videoFile = result.stdout
    starttime = 0
    if 't=' in url:
        starttime = url.split('t=')[1]
    starttime = str(datetime.timedelta(seconds=int(starttime)))
    resultFile = '%s_cut.mp4' % videoFile
    cut_video(videoFile, starttime, clipDuration, resultFile)
    videoFile = resultFile
    with open(videoFile, 'rb') as file:
        success_video(update, context, file.read(), url)


def success_video(update: Update, context: CallbackContext, video: str | bytes, url: str):
    if update.effective_chat is not None:
        message = context.bot.send_video(
            chat_id=update.effective_chat.id, video=video)
        if update.effective_chat.type != Chat.PRIVATE:
            context.bot.edit_message_caption(
                chat_id=update.effective_chat.id, message_id=message.message_id,
                caption='<a href="tg://user?id=%s">%s</a>\n<a href="%s">%s</a>' % (
                    update.message.from_user.id, update.message.from_user.full_name, url, url),
                parse_mode=ParseMode.HTML
            )
    else:
        context.bot.send_message(
            chat_id=dima_chat_id, text="WTF: %s\n%s\n%s" % (url, update, context))
        context.bot.send_video(
            chat_id=dima_chat_id, video=video, reply_to_message_id=update.message.message_id)
