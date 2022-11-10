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
pool = Pool(10)

bot = commands.Bot(command_prefix = "!")
activity = discord.Streaming(name = "Версия 0.1 Alpha", url = "https://twitch.tv/discord")

async def spam_webhooks(spamtext, webhook):
    data = {
        "content": str(spamtext)
    }
    pool.apply_async(requests.post, args=[webhook], kwds={'data': data})

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

@bot.slash_command(description = "Начать спам пользователю в канал и в лс")
async def spam(ctx, member: discord.Member, spamtext: str = None, messagecount: int = 5, spamyourself: bool = False):
    # Команда для спама пользователю
    """
    for tokens in config.spam_tokens:
        print(tokens)
    """
    await ctx.send('[LOG] Запуск спама...')

    message = await ctx.channel.send(f'-- START LOG ({ctx.author.id}) --\n[LOG] Запуск спама...')
    if ctx.author.id == member.id:
        if spamyourself == False:
            message = await message.edit(message.content + f"\n[ERROR] Нельзя спаммить себе, но вы можете включить параметр spamyourself на True\n -- END LOG ({ctx.author.id}) --")
            return
        else:
            message = await message.edit(message.content + f"\n[WARN] В основном спаммить себе нельзя, но если вы так захотели: пожалуйста!")

    if spamtext == None:
        spamtext = f"** **\nВас заспаммили, {member.mention}!\nХочешь также? Смотри общие сервера бота, и спамь другим лс абсолютно бесплатно!"
    spamtext = f"{member.mention} " + spamtext
    message = await message.edit(message.content + '\n[LOG] Идёт спам в лс')
    
    try:
        for x in range(messagecount):
            await member.send(spamtext)
        message = await message.edit(message.content + "\n[LOG] Спам в лс прошёл, идёт спам вебхуками")
    except:
        message = await message.edit(message.content + '\n[ERROR] Спам в лс не удался, лс был закрыт, или рейт лимиты')
    
    message = await message.edit(message.content + '\n[LOG] Идёт спам вебхуками (P.S: Из за обновления алгоритмов спама, сообщений даже чуть больше чем указано)')

    for x in range(messagecount):
        await spam_webhooks(spamtext = spamtext, webhook = random.choice(config.spam_webhooks))
        #threading.Thread(target = spam, args = (spamtext == spamtext, webhook == webhook)).start()

    message = await message.edit(message.content + "\n[LOG] Спам вебхуками прошёл")
    message = await message.edit(message.content + f"\n[LOG] Спам прошёл\n -- END LOG ({ctx.author.id}) --")

bot.run(token = config.bot_token)