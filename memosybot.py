# -*- coding: utf-8 -*-
from telegram import Update, Bot, MessageEntity, Message
from telegram.ext import MessageHandler, Filters, CallbackContext, Updater
from telegram.error import BadRequest, NetworkError
import logging
import sys
import video_parsers
dima_chat_id = 293554686


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
                try_function(video_parsers.youtube_parse, update, context, url,
                             update=update, context=context
                             )


def error_message(*args, update: Update, context: CallbackContext):
    if update.effective_chat is not None:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сорян, сегодня не мой день ¯\\_(ツ)_/¯",
            reply_to_message_id=update.message.message_id
        )
    bot = Bot(token)
    bot.send_message(
        chat_id=dima_chat_id, text="WTF: %s\n%s\n%s\n%s" % ((sys.exc_info()), update, context, args))


def try_function(function, *args, update: Update, context: CallbackContext):
    loadingMessageId = ''
    if update.effective_chat is not None:
        loadingMessage = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='🤔',
            entities=[MessageEntity(type=MessageEntity.CUSTOM_EMOJI,
                                    offset=0, length=2, custom_emoji_id='5465608036078852982')],
            reply_to_message_id=update.message.message_id
        )
        loadingMessageId = loadingMessage.message_id
    x = 0
    while x < 10:
        try:
            function(*args)
        except BadRequest:
            pass
            break
        except NetworkError:
            x += 1
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
            chat_id=update.effective_chat.id, message_id=loadingMessageId)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    with open('token', 'r') as t:
        global token
        token = t.read()
    url_handler = MessageHandler(Filters.text & (~Filters.command), url_parse)
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(url_handler)
    updater.start_polling()
