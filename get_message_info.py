import logging
import settings
from telegram import MessageEntity, Update
from telegram.ext import MessageHandler, Filters, CallbackContext, Updater


def log_info(update: Update, context: CallbackContext):
    # context.bot.send_message(
    #     chat_id=settings.debug_chat_id, text=update.to_json)
    print(update.message)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    settings.init()
    log = MessageHandler(filters=Filters.all, callback=log_info)
    updater = Updater(token=settings.token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(log)
    updater.start_polling()
