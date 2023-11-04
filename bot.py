from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from common import create_short_url, short_url_to_long, get_all_user_urls

bot = AsyncTeleBot('6635154404:AAGWO6DvvBHUFuI1ue_ZqEWiQDX46uhnQLI')



# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
Hi there, I am EchoBot.
I am here to echo your kind words back to you. Just say anything nice and I'll say the exact same thing to you!\
""")

@bot.message_handler(commands=['create'])
async def create_short(message: Message):
    long_url = message.text.replace('/create ', '')
    user_id = message.from_user.id
    short_url = await create_short_url(long_url, user_id=user_id)
    await bot.reply_to(message, short_url)


@bot.message_handler(commands=['get_all'])
async def get_user_url(message: Message):
    user_id = message.from_user.id
    url_info = await get_all_user_urls(user_id=user_id)
    all_urls = [f"{link['short_url']} -> {link['long_url']}" for link in url_info]
    await bot.send_message(message.chat.id, '\r\n'.join(all_urls)) if all_urls else 'You have no links'
@bot.message_handler(func=lambda message: True)
async def get_long_url(message: Message):
    long_url = await short_url_to_long(message.text)
    await bot.reply_to(message, long_url)


import asyncio
asyncio.run(bot.polling())