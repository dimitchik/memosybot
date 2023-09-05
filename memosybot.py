# -*- coding: utf-8 -*-
import settings
import video_parsers
import json
import logging
from telegram.error import BadRequest, NetworkError
from telegram.ext import MessageHandler, Filters, CallbackContext, Updater, Dispatcher
from telegram import Update, Bot, MessageEntity, Message
from os import path
import sys
import queue

here = path.dirname(path.realpath(__file__))
sys.path.append(path.join(here, "./vendored"))


def webhook(event, _):
    settings.init()
    try:
        bot = Bot(settings.token)
        update = Update.de_json(json.loads(event['body']), bot)
        context = CallbackContext(dispatcher=Dispatcher(bot, queue.Queue()))
        if update is None:
            return {"statusCode": 200}
        url_parse(update, context)
    except Exception as e:
        print(e)
        error_message(e)
    return {"statusCode": 200}


def url_parse(update: Update, context: CallbackContext):
    if update.message.entities:
        for entity in update.message.entities:
            url = update.message.parse_entity(entity)
            if '9gag.com' in url and not url.endswith('.mp4'):
                try_function(video_parsers.ninegag_parse, update, context, url,
                             update=update, context=context
                             )
            if 'coub.com' in url or 'coub.ru' in url:
                try_function(video_parsers.coub_parse, update, context, url,
                             update=update, context=context
                             )
            if 'youtu.be' in url or 'youtube.com' in url:
                if 'clip' in url:
                    try_function(video_parsers.youtube_clip_parse, update,
                                 context, url, update=update, context=context
                                 )
                else:
                    try_function(video_parsers.youtube_parse, update, context, url,
                                 update=update, context=context
                                 )
            if 'reddit.com' in url or 'v.redd.it' in url:
                try_function(video_parsers.reddit_parse, update,
                             context, url, update=update, context=context)
            if 'tiktok.com' in url:
                try_function(video_parsers.tiktok_parse, update,
                             context, url, update=update, context=context)


def error_message(*args, update: Update | None = None, context: CallbackContext | None = None):
    import traceback
    bot = Bot(settings.token)
    if update is not None and update.effective_chat is not None:
        bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сорян, сегодня не мой день ¯\\_(ツ)_/¯",
            reply_to_message_id=update.message.message_id
        )
    bot = Bot(settings.token)
    bot.send_message(
        chat_id=settings.debug_chat_id,
        text="WTF: %s\n Additional info: %s" % (traceback.format_exc(), args))


def try_function(function, *args, update: Update, context: CallbackContext):
    loading_message_id = ''
    if update.effective_chat is not None:
        loading_message = context.bot.send_sticker(
            chat_id=update.effective_chat.id,
            sticker='CAACAgIAAxkBAAIBzGOHjfCGEPoiv6G2LCxCLUHjemF8AAJBAQACzRswCPHwYhjf9pZYKwQ',
            disable_notification=True,
        )
        loading_message_id = loading_message.message_id
    x = 0
    while x < 10:
        print(x)
        try:
            function(*args)
        except BadRequest:
            pass
            break
        except NetworkError:
            x += 1
            print(sys.exc_info())
            continue
        except:
            error_message(
                *args, update=update, context=context)
        break
    else:
        error_message(
            *args, update=update, context=context)
    if update.effective_chat is not None:
        context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=loading_message_id)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    settings.init()
    url_handler = MessageHandler(Filters.text & (
        ~Filters.command) & Filters.entity(MessageEntity.URL), url_parse)
    updater = Updater(token=settings.token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(url_handler)
    updater.start_polling()
