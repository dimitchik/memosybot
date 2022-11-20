# -*- coding: utf-8 -*-
from telegram import Update, Bot, ParseMode
from telegram.ext import MessageHandler, Filters, CallbackContext, Updater
from telegram.error import BadRequest, NetworkError
import logging
import sys
import parsers
dima_chat_id = 293554686


def url_parse(update: Update, context: CallbackContext):
    if update.message.entities:
        for entity in update.message.entities:
            url = update.message.parse_entity(entity)
            if '9gag.com' in url and not url.endswith('.mp4'):
                try_function(parsers.ninegag_parse, update, context, url,
                             update=update, context=context)
            if 'coub.com' in url or 'coub.ru' in url:
                try_function(parsers.coub_parse, update, context, url,
                             update=update, context=context)


def success_video(update: Update, context: CallbackContext, video: str | bytes, url: str):
    if update.effective_chat is not None:
        message = context.bot.send_video(
            chat_id=update.effective_chat.id, video=video)
        context.bot.edit_message_caption(
            chat_id=update.effective_chat.id, message_id=message.message_id, caption='<a href="tg://user?id=%s">%s</a>\n<a href="%s">%s</a>' % (update.message.from_user.id, update.message.from_user.full_name, url, url), parse_mode=ParseMode.HTML)
    else:
        context.bot.send_message(
            chat_id=dima_chat_id, text="WTF: %s\n%s\n%s" % (url_parse, update, context))
        context.bot.send_video(
            chat_id=dima_chat_id, video=video, reply_to_message_id=update.message.message_id)


def error_message(*args, update: Update | None, context: CallbackContext | None):
    if update is not None and update.effective_chat is not None and context is not None:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Сорян, сегодня не мой день ¯\\_(ツ)_/¯", reply_to_message_id=update.message.message_id)
    bot = Bot(token)
    bot.send_message(
        chat_id=dima_chat_id, text="WTF: %s\n%s\n%s\n%s" % ((sys.exc_info()), update, context, args))


def try_function(function, *args, update: Update | None, context: CallbackContext | None):
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
