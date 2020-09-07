import os

from telegram.ext import Updater, CommandHandler

from settings.settings_local import TG_TOKEN

# File logic
filename = '../tg_ids'

if not os.path.exists(filename):
    open(filename, 'a').close()


def get_saved_chat_ids():
    with open(filename, 'r+') as f:
        content = f.read()

        return [int(i) for i in content.split(';')] if content else []


def write_new_chat_ids(ids):
    with open(filename, 'w+') as f:
        f.write(';'.join((str(i) for i in ids)))


# Bot logic
updater = Updater(token=TG_TOKEN, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


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


start_handler = CommandHandler('start', start)
register_handler = CommandHandler('register', register)
stop_handler = CommandHandler('stop', stop)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(register_handler)
dispatcher.add_handler(stop_handler)


def send_messages(text):
    ids = get_saved_chat_ids()
    for id in ids:
        updater.bot.send_message(id, text)
