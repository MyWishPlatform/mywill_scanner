from telegram.ext import Updater, CommandHandler

from settings import settings_local
from .storage import get_saved_chat_ids, write_new_chat_ids


def start(update, context):
    text = ("Hi! I'm alert bot for one of scanner projects\n"
            "I have several commands, like:\n\n"
            "/register - you subscibing into my spam hell\n\n"
            "/stop - i will stop send you all this logs\n\n"
            "With these commands you can start me here "
            "or inside a chat with your friends.\n"
            "You can all enjoy my bug reports! "
            )
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def register(update, context):
    chat_id = update.effective_chat.id
    lines = get_saved_chat_ids()
    if chat_id not in get_saved_chat_ids():
        lines.append(chat_id)
        write_new_chat_ids(lines)
        text = "You subscribed on errors, spam will start soon"
    else:
        text = 'What do you want?! You already subscribed!'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def stop(update, context):
    chat_id = update.effective_chat.id
    lines = get_saved_chat_ids()
    if chat_id in lines:
        lines.remove(chat_id)
        write_new_chat_ids(lines)
        text = "You unsubscribed on errors, feel free.. for now 😈"
    else:
        text = 'You do not even subscribed! Fukoff!'

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


class AlertBot:
    def __init__(self):
        token = getattr(settings_local, 'TELEGRAM_TOKEN', None)
        if not token:
            self.updater = None
            print('WARNING! Cant start bot without token in settings', flush=True)
            return

        self.updater = Updater(token=token, use_context=True)
        dispatcher = self.updater.dispatcher

        start_handler = CommandHandler('start', start)
        register_handler = CommandHandler('register', register)
        stop_handler = CommandHandler('stop', stop)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(register_handler)
        dispatcher.add_handler(stop_handler)

    def start_polling(self):
        if not self.updater:
            return

        self.updater.start_polling()

    def send_messages(self, text):
        if not self.updater:
            return

        ids = get_saved_chat_ids()
        for id in ids:
            self.updater.bot.send_message(id, text)


alert_bot = AlertBot()
