# 檔案名稱: bot.py

import discord
from discord.ext import tasks, commands
import asyncio
import os

# 從環境變數讀取 Token，這是部署到雲端的標準做法
# 如果環境變數不存在，則會回傳 None，使程式在啟動時就失敗，避免使用無效 Token
TOKEN = os.getenv('DISCORD_TOKEN')

# 你指定要傳送的 GIF 的 URL
SPECIFIC_GIF_URL = 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExc2psYXkxZmdlajJmajI0NWtkeHhna2ZqYTltODg0c2lrZTVmY3E2dyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/qC23gGBlrqENgb3ENs/giphy.gif'

# 設置 intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 狀態旗標
is_sleeping = False
sleep_timer_task = None

@bot.event
async def on_ready():
    print(f'以 {bot.user.name} 的身分登入')
    send_messages_hourly.start()

async def send_the_messages(channel):
    try:
        if SPECIFIC_GIF_URL:
            await channel.send('喝水水')
            await channel.send('<:swallow:1392204204252332113>')
            await channel.send(SPECIFIC_GIF_URL)
            print(f"已在頻道 '{channel.name}' 傳送提醒。")
        else:
            print("未設定 GIF URL。")
    except discord.errors.Forbidden:
        print(f"錯誤：沒有在頻道 '{channel.name}' 中傳送訊息的權限。")
    except Exception as e:
        print(f"傳送訊息時發生錯誤: {e}")

@tasks.loop(hours=1)
async def send_messages_hourly():
    global is_sleeping
    if is_sleeping:
        print("機器人正在睡覺中，跳過此次傳送。")
        return

    channel_to_send = None
    for guild in bot.guilds:
        for text_channel in guild.text_channels:
            if text_channel.permissions_for(guild.me).send_messages:
                channel_to_send = text_channel
                break
        if channel_to_send:
            break

    if channel_to_send:
        await send_the_messages(channel_to_send)
    else:
        print("沒有找到可以傳送訊息的頻道。")

@bot.command(name='sleep')
@commands.has_permissions(administrator=True)
async def sleep_bot(ctx):
    global is_sleeping, sleep_timer_task
    if is_sleeping:
        await ctx.send("睡你媽逼，吵三小\n<:red:1370035786606579833>")
        return
    is_sleeping = True
    await ctx.send("晚安，瑪卡巴卡，逼餔了\n<:dead:1406651349751304263>")
    print("機器人進入睡覺模式。")
    async def wake_up():
        global is_sleeping
        await asyncio.sleep(8 * 60 * 60)
        if is_sleeping:
            is_sleeping = False
            print("機器人已從睡覺模式中醒來。")
            if ctx.channel:
                await ctx.channel.send("瓜瓜\n<:xixi:1359747364646162472>")
    sleep_timer_task = asyncio.create_task(wake_up())

@bot.command(name='wake')
@commands.has_permissions(administrator=True)
async def wake_bot(ctx):
    global is_sleeping, sleep_timer_task
    if not is_sleeping:
        await ctx.send("<:bruh:1386927657937145856>")
        return
    is_sleeping = False
    if sleep_timer_task:
        sleep_timer_task.cancel()
        sleep_timer_task = None
    await ctx.send("瓜瓜\n<:bright:1370035857100111972>")
    print("機器人被手動喚醒。")
    await send_the_messages(ctx.channel)
    send_messages_hourly.restart()
    await ctx.send("已傳送提醒，並重設計時器。")

if TOKEN is None:
    print("錯誤：請設定 DISCORD_TOKEN 環境變數！")
else:
    bot.run(TOKEN)