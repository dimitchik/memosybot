
from telegram import Update, Chat, Bot
import requests
import urllib.request
import os
from media import get_length, loop_video, loop_audio, download_stream_start_dur, download_stream
import settings

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


async def ninegag_parse(update: Update, bot: Bot, url: str):
    id = url.split('/')[-1]
    if '?' in id:
        id = id.split('?')[0]
    videoUrl = 'https://img-9gag-fun.9cache.com/photo/%s_460svh265.mp4' % (id)
    try:
        requests.get(videoUrl, headers=headers).raise_for_status()
        await success_video(update, bot, videoUrl, url)
    except:
        import traceback
        from firebase_functions import logger
        logger.error("WTF: %s\n Additional info: %s" % (traceback.format_exc(), url))
        return

async def coub_parse(update: Update, bot: Bot, url: str):
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
            await success_video(update, bot, file.read(), url)


async def youtube_parse(update: Update, bot: Bot, url: str):
    from yt_dlp import YoutubeDL
    def logProgressHook(d):
        if d['status'] == 'finished':
            logger.info('Done downloading, now converting ...')
        elif d['status'] == 'downloading':
            logger.info('Downloading video %s of size %s' % (d['downloaded_bytes'], d['total_bytes']))
        elif d['status'] == 'error':
            logger.error('Error downloading video %s' % d['error'])
        else:
            logger.info('Unknown status %s' % d['status'])
    def logPostProcessHook(d):
        if d['status'] == 'started':
            logger.info('Post-processing started')
        elif d['status'] == 'processing':
            logger.info('Post-processing on progress')
        elif d['status'] == 'finished':
            logger.info('Post-processing finished')
        else:
            logger.info('Unknown status %s' % d['status'])
    from firebase_functions import logger
    try:
        def range(_, __):
            if url.split('t=')[-1] == url:
                timestamp = 0
            else:
                timestamp = int(url.split('t=')[1].split('&')[0])
            return [{'start_time': timestamp, 'end_time': timestamp+60}]
        from io import StringIO
        import sys
        sys.stdout = mystdout = StringIO()
        with YoutubeDL({
            'outtmpl': {'default': '/tmp/output.mp4'},
            'format': '(b[fps>30]/b)[height<=720][ext=mp4]/(w[fps>30][ext=mp4]/w[ext=mp4]/w)',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            # 'quiet': True,
            'verbose': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'prefer_ffmpeg': True,
            'progress_hooks': [logProgressHook],
            'postprocessor_hooks': [logPostProcessHook],
            'max_filesize': 100000000,
            'download_ranges': range,
            'cookiefile': 'cookies.txt',
        }) as ydl:
            ydl.download([url])
        mystdout.seek(0)
        logger.info(mystdout.read())
        import ffmpeg
        video_streams = ffmpeg.probe('/tmp/output.mp4', select_streams = "v")
        width = video_streams['streams'][0]['width']
        height = video_streams['streams'][0]['height']
        with open('/tmp/output.mp4', 'rb') as file:
            await success_video(update, bot, file.read(), url, width=width, height=height)
    except:
        import traceback
        logger.error("WTF: %s\n Additional info: %s" % (traceback.format_exc(), url))
    finally:
        sys.stdout = sys.__stdout__

async def success_video(update: Update, bot: Bot, video: str | bytes, url: str, width: int | None = None, height: int | None = None):
    try:
        if update.effective_chat is not None:
            message = await bot.send_video(
                chat_id=update.effective_chat.id, video=video, width=width, height=height)
            if update.effective_chat.type != Chat.PRIVATE:
                await bot.edit_message_caption(
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
            import traceback
            from firebase_functions import logger
            logger.error("WTF: %s\n Additional info: %s" % (traceback.format_exc(), video))
            await bot.send_message(
                chat_id=settings.debug_chat_id, text="WTF: %s\n%s\n%s" % (url, update))
            await bot.send_video(
                chat_id=settings.debug_chat_id, video=video, reply_to_message_id=update.message.message_id)
        if isinstance(video, str) and os.path.exists(video) and not video.startswith('http'):
            os.remove(video)
    except:
        import traceback
        from firebase_functions import logger
        logger.error("WTF: %s\n Additional info: %s" % (traceback.format_exc(), video))
