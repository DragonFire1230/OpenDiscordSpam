"""
Copyright DragonFire Community 2020-2022

Этот файл содержит основной код проекта OpenDiscordSpam
Цель проекта: Сделать свободную реализацию спаммилки с нескольких аккаунтов
"""

import disnake as discord
from disnake.ext import commands
import random
#from httpx import AsyncClient
#requests = AsyncClient()
import requests
#import threading
import config
from multiprocessing.dummy import Pool
import json
pool = Pool(10)

bot = commands.Bot(command_prefix = "!")
activity = discord.Streaming(name = "Версия 0.2 Beta", url = "https://twitch.tv/discord")

async def spam_dm(spamtext, id, token):
    f = open(f"./cache_users/{id}.json", "r")
    data = json.loads(f.read())

    payload = {"content" : spamtext, "tts" : False}
    headers = {
        "authorization": "Bot " + token
    }
    pool.apply_async(requests.post, args=[f"https://discord.com/api/v6/channels/{data[token]}/messages"], kwds={'headers': headers, 'json': payload})

#async def spam_webhooks(spamtext, webhook):
#    data = {
#        "content": str(spamtext)
#    }
#    pool.apply_async(requests.post, args=[webhook], kwds={'data': data})

@bot.after_slash_command_invoke
@bot.after_user_command_invoke
@bot.after_message_command_invoke
async def after_commands_invoke(ctx):
	print(f'[Спам] Выполнил: {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})')


@bot.event
async def on_ready():
    print('Бот работает!')
    await bot.change_presence(
        status = discord.Status.online,
        activity = activity
    )

@bot.slash_command(description = "Получить Recipient ID для спама")
async def get_recipient_id(ctx, member: discord.Member):
    await ctx.send('[LOG] Запуск...')
    message = await ctx.channel.send(f'-- START LOG ({ctx.author.id}) --\n[LOG] Подождите...')
    inputJson = json.loads('{}')
    for token in config.spam_tokens:
        retries = 0
        headers = {
            "authorization": "Bot " + token
        }
        payload = {'recipient_id': member.id}
        src = pool.apply_async(requests.post, args=["https://discord.com/api/v6/users/@me/channels"], kwds={'headers': headers, 'json': payload}).get()
        print(src.content)
        dm_json = json.loads(src.content)
        inputJson = inputJson | {
            f"{token}": f"{dm_json['id']}"
        }
    json.dump(inputJson, open(f"./cache_users/{member.id}.json", "w"), sort_keys=True, indent=4)
    message = await message.edit(message.content + f'\n[LOG] Recipient ID пользователя {member.name} записан в кэш, запустите спам')

@bot.slash_command(description = "Начать спам пользователю в канал и в лс")
async def spam(ctx, member: discord.Member, spamtext: str = None, messagecount: int = 5):
    # Команда для спама пользователю
    """
    for tokens in config.spam_tokens:
        print(tokens)
    """
    await ctx.send('[LOG] Запуск спама...')

    message = await ctx.channel.send(f'-- START LOG ({ctx.author.id}) --\n[LOG] Запуск спама...')

    if spamtext == None:
        spamtext = f"** **\nВас заспаммили!\nХочешь также? Смотри общие сервера бота, и спамь другим лс абсолютно бесплатно!"
    message = await message.edit(message.content + '\n[LOG] Идёт спам в лс')

    for token in config.spam_tokens:
        for x in range(messagecount):
            await spam_dm(spamtext, member.id, token)
    #message = await message.edit(message.content + "\n[LOG] Спам в лс прошёл, идёт спам вебхуками")

    #message = await message.edit(message.content + '\n[LOG] Идёт спам вебхуками (P.S: Из за обновления алгоритмов спама, сообщений даже чуть больше чем указано)')

    #for x in range(messagecount):
    #await spam_webhooks(spamtext = spamtext, webhook = random.choice(config.spam_webhooks))
    #threading.Thread(target = spam, args = (spamtext == spamtext, webhook == webhook)).start()

    message = await message.edit(message.content + "\n[LOG] Спам в лс прошёл")
    message = await message.edit(message.content + f"\n[LOG] Спам прошёл\n -- END LOG ({ctx.author.id}) --")

bot.run(token = config.bot_token)
