from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext, Updater
import requests
import urllib.request
import os
from media import get_length, loop_video, loop_audio
from memosybot import success_video

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
    videoUrl = 'https://9gag.com/photo/%s_460sv.mp4' % (id)
    requests.get(videoUrl, headers=headers)
    success_video(update, context, videoUrl, url)
