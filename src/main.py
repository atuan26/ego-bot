import os
import sys
import threading
import time

import telebot
from dotenv import load_dotenv
from telebot import types

load_dotenv()

from ego import Response, get_room_status

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")

bot = telebot.TeleBot(TG_BOT_TOKEN)

MAX_ROOM_RESULT = int(os.getenv("MAX_ROOM_RESULT", 5))
EXCLUDE_ROOM_ID = [151, 54, 158]
SLEEP = int(os.getenv("SLEEP", 3))
RECEIVER = []


@bot.message_handler(commands=["off"])
def off(message):
    if message.chat.id in RECEIVER:
        RECEIVER.remove(message.chat.id)
    bot.reply_to(message, "Notification OFF\n/on")


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    if message.chat.id not in RECEIVER:
        RECEIVER.append(message.chat.id)
    bot.reply_to(message, "Howdy, how are you doing? Turn ON notification with /on")


@bot.message_handler(commands=["on"])
def on(message):
    if message.chat.id not in RECEIVER:
        RECEIVER.append(message.chat.id)
    bot.reply_to(message, "Notification ON\n/off")


def send_room_status():
    res: Response = get_room_status()

    #print(res)
    available_rooms = [
        room for room in res.available_rooms if room.id not in EXCLUDE_ROOM_ID
    ][:MAX_ROOM_RESULT]

    print(f"Availalble room: {len(available_rooms)}, reciver: {RECEIVER}")
    if len(available_rooms) > 0:
        print(Response.build_message(available_rooms))
    for room in available_rooms:
        button_text = "Mark as joined"
        button_value = f"join#{room.name}"
        button = types.InlineKeyboardButton(
            text=button_text, callback_data=button_value
        )
        message_text = room.avaiable_message
        reply_markup = types.InlineKeyboardMarkup(row_width=1)
        reply_markup.add(button)
        for r in RECEIVER:
            bot.send_message(r, message_text, reply_markup=reply_markup)
    if (len(res.available_rooms) - MAX_ROOM_RESULT) > 0:
        for r in RECEIVER:
            bot.send_message(r, f"+{len(res.available_rooms) - MAX_ROOM_RESULT} others")


@bot.callback_query_handler(func=lambda call: True)
def handle_join_room(call):
    callback_data, room = call.data.split("#")
    call_user = call.from_user
    if callback_data == "join" and call_user.id in RECEIVER:
        RECEIVER.remove(call_user.id)
        bot.send_message(call_user.id, f"You joined {room}\n\nNotification OFF\n/on")
        for r in RECEIVER:
            bot.send_message(r, f"📣{call_user.username} just joined #{room}")


def cronJob():
    while True:
        send_room_status()
        time.sleep(SLEEP)


added_thread = threading.Thread(target=cronJob, name="new_added_thread")
added_thread.start()
bot.infinity_polling()
