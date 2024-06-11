# -*- coding: utf-8 -*-
import settings
import video_parsers
import json
import logging
from telegram.error import BadRequest, NetworkError
from telegram.ext import MessageHandler, ApplicationBuilder, filters, CallbackContext, Updater
from telegram import Update, Bot, MessageEntity, Message
from os import path
import sys
import queue

here = path.dirname(path.realpath(__file__))
sys.path.append(path.join(here, "./vendored"))

async def url_parse(update: Update, bot: Bot):
    if not update.message:
        return
    if update.message.entities:
        for entity in update.message.entities:
            url = update.message.parse_entity(entity)
            if '9gag.com' in url and not url.endswith('.mp4'):
                await try_function(video_parsers.ninegag_parse, update, bot, url,)
            elif 'coub.com' in url or 'coub.ru' in url:
                await try_function(video_parsers.coub_parse, update, bot, url,)
            elif 'youtu.be' in url or 'youtube.com' in url:
                # if 'clip' in url:
                #     try_function(video_parsers.youtube_clip_parse, update,
                #                  bot, url, update=update, bot=bot
                #                  )
                # else:
                await try_function(video_parsers.youtube_parse, update, bot, url)
            # if 'reddit.com' in url or 'v.redd.it' in url:
            #     await try_function(video_parsers.reddit_parse, update, bot, url)
            else:
                await try_function(video_parsers.youtube_parse, update, bot, url)


async def error_message(*args, update: Update | None = None):
    import traceback
    bot = Bot(settings.token)
    if update is not None and update.effective_chat is not None:
        await bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сорян, сегодня не мой день ¯\\_(ツ)_/¯",
            reply_to_message_id=update.message.message_id
        )
    bot = Bot(settings.token)
    await bot.send_message(
        chat_id=settings.debug_chat_id,
        text="WTF: %s\n Additional info: %s" % (traceback.format_exc(), args))
    logger.error("WTF: %s\n Additional info: %s" % (traceback.format_exc(), args))


async def try_function(function, *args):
    # loading_message = None
    # if update.effective_chat is not None:
    #     loading_message = await context.bot.send_sticker(
    #         chat_id=update.effective_chat.id,
    #         sticker='CAACAgIAAxkBAAIBzGOHjfCGEPoiv6G2LCxCLUHjemF8AAJBAQACzRswCPHwYhjf9pZYKwQ',
    #         disable_notification=True,
    #     )
    # x = 0
    # while x < 10:
        # print("Attempt %s" % x)
    try:
        await function(*args)
    except BadRequest:
        pass
        # break
    except NetworkError:
        pass
        # continue
    except:
        
        # break
        pass
        await error_message(*args)
    # break
    # else:
    #     await error_message(
    #         *args, update=update, context=context)
    # if loading_message is not None:
    #     await loading_message.delete()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    settings.init()
    app =ApplicationBuilder().token(settings.token).build()
    url_handler = MessageHandler(filters.TEXT & (
        ~filters.COMMAND) & filters.Entity(MessageEntity.URL), url_parse)
    app.add_handler(url_handler)
    app.run_polling()
