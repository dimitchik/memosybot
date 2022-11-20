# -*- coding: utf-8 -*-
import os
import subprocess
import requests
from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext, Updater, CommandHandler
import logging
import sys
import telegram
import telegram.error
import urllib.request
dima_chat_id = 293554686

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def url_parse(update: Update, context: CallbackContext):
    if update.message.entities:
        for entity in update.message.entities:
            url = update.message.parse_entity(entity)
            if '9gag.com' in url and not url.endswith('.mp4'):
                try_function(ninegag_parse, update, context, url,
                             update=update, context=context)
            if 'coub.com' in url or 'coub.ru' in url:
                try_function(coub_parse, update, context, url,
                             update=update, context=context)


def success_video(update: Update, context: CallbackContext, video: str | bytes, url: str):
    if update.effective_chat is not None:
        message = context.bot.send_video(
            chat_id=update.effective_chat.id, video=video)
        context.bot.edit_message_caption(
            chat_id=update.effective_chat.id, message_id=message.message_id, caption='<a href="tg://user?id=%s">%s</a>\n<a href="%s">%s</a>' % (update.message.from_user.id, update.message.from_user.full_name, url, url), parse_mode=telegram.ParseMode.HTML)
    else:
        context.bot.send_message(
            chat_id=dima_chat_id, text="WTF: %s\n%s\n%s" % (url_parse, update, context))
        context.bot.send_video(
            chat_id=dima_chat_id, video=video, reply_to_message_id=update.message.message_id)


def error_message(*args, update: Update | None, context: CallbackContext | None):
    if update is not None and update.effective_chat is not None and context is not None:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Сорян, сегодня не мой день ¯\\_(ツ)_/¯", reply_to_message_id=update.message.message_id)
    bot = telegram.Bot(token)
    bot.send_message(
        chat_id=dima_chat_id, text="WTF: %s\n%s\n%s\n%s" % ((sys.exc_info()), update, context, args))


def try_function(function, *args, update: Update | None, context: CallbackContext | None):
    x = 0
    while x < 10:
        try:
            function(*args)
        except telegram.error.BadRequest:
            pass
            break
        except telegram.error.NetworkError:
            x += 1
            continue
        except:
            error_message(
                *args, update=update, context=context)
        break
    else:
        error_message(
            *args, update=update, context=context)


def ninegag_parse(update: Update, context: CallbackContext, url: str):
    id = url.split('/')[-1]
    videoUrl = 'https://9gag.com/photo/%s_460sv.mp4' % (id)
    requests.get(videoUrl, headers=headers)
    success_video(update, context, videoUrl, url)


def get_length(input: str) -> int:
    from pymediainfo import MediaInfo
    media_info = MediaInfo.parse(input)
    duration_in_ms = media_info.tracks[0].duration  # type: ignore
    return duration_in_ms


def loop_video(video: str, audio: str, result: str):
    subprocess.run(['ffmpeg',  '-stream_loop', '-1', '-i', video, '-i', audio, '-shortest',
                   '-map', '0:v:0', '-map', '1:a:0', '-y', """%s""" % result], encoding='utf-8-sig')


def loop_audio(video: str, audio: str, result: str):
    subprocess.run(['ffmpeg', '-i', video, '-stream_loop', '-1', '-i', audio, '-shortest',
                   '-map', '0:v:0', '-map', '1:a:0', '-y', """%s""" % result], encoding='utf-8-sig')


def coub_parse(update: Update, context: CallbackContext, url: str):
    id = url.split('/')[-1]
    requestUrl = 'https://coub.com/api/v2/coubs/%s' % (id)
    response = requests.get(requestUrl, headers=headers)
    if response._content is not None:
        response.raise_for_status()
        params = response.json()
        videoUrl = params['file_versions']['mobile']['video']
        print(videoUrl)
        videoFile = urllib.request.urlretrieve(
            videoUrl)[0]
        videoFile = os.path.abspath(videoFile)
        print(videoFile)
        audioUrl = params['file_versions']['mobile']['audio'][0]
        audioFile = urllib.request.urlretrieve(
            audioUrl)[0]
        audioFile = os.path.abspath(audioFile)
        print(audioFile)
        videoLength = get_length(videoFile)
        print('video length: %s' % videoLength)
        audioLength = get_length(audioFile)
        print('audio length: %s' % audioLength)
        result = '%s_merged.mp4' % videoUrl.split(
            '/')[-1].split('.')[0]
        result = os.path.abspath(result)
        if audioLength > videoLength:
            loop_video(videoFile, audioFile, result)
        else:
            loop_audio(videoFile, audioFile, result)
        with open(result, 'rb') as file:
            success_video(update, context, file.read(), url)


if __name__ == '__main__':
    with open('token', 'r') as t:
        global token
        token = t.read()
    url_handler = MessageHandler(Filters.text & (~Filters.command), url_parse)
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(url_handler)
    updater.start_polling()
