import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL

API_ID = 37215268
API_HASH = 0fc3e1a1637d65c660672554aecfa23b
BOT_TOKEN = 8888943383:AAG_gTwvjIFbdXL0qmDPwOl2VZbaBloEo5w

app = Client("Blublu", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

queue = {}
ydl_opts = {"format": "bestaudio", "noplaylist": True, "quiet": True}

def search_song(query):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        video = info['entries'][0]
        return video['title'], video['url'], video['webpage_url']

async def play_next(chat_id):
    if queue.get(chat_id):
        title, url, link = queue[chat_id].pop(0)
        await call.play(chat_id, MediaStream(url))
        return title
    return None

@app.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply(
        "🎵 **Blublu Music Bot** 🎵\n\n"
        "Commands:\n"
        "/play <song> - Gana bajao\n"
        "/pause - Roko\n"
        "/resume - Phir chalao\n"
        "/skip - Agla gana\n"
        "/stop - Band karo\n"
        "/queue - List dekho"
    )

@app.on_message(filters.command("play"))
async def play(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("Gaane ka naam likho! Eg: /play Diljit - Born To Shine")
    if not m.from_user:
        return
    chat_id = m.chat.id
    query = " ".join(m.command[1:])
    msg = await m.reply(f"🔍 Dhoond raha hu: {query}...")
    try:
        title, url, link = search_song(query)
    except Exception as e:
        return await msg.edit(f"Error aa gaya: {e}")
    
    if chat_id not in queue:
        queue[chat_id] = []
    queue[chat_id].append((title, url, link))

    if len(queue[chat_id]) == 1:
        try:
            await call.play(chat_id, MediaStream(url))
            await msg.edit(f"▶️ **Ab baj raha hai:**\n{title}\n🔗 {link}")
        except Exception as e:
            await msg.edit(f"Pehle mujhe Voice Chat me add karo aur /play dobara likho.\nError: {e}")
    else:
        await msg.edit(f"➕ Queue me add ho gaya:\n{title}")

@app.on_message(filters.command("pause"))
async def pause(_, m: Message):
    await call.pause(m.chat.id)
    await m.reply("⏸️ Pause kar diya")

@app.on_message(filters.command("resume"))
async def resume(_, m: Message):
    await call.resume(m.chat.id)
    await m.reply("▶️ Phir se chala diya")

@app.on_message(filters.command("skip"))
async def skip(_, m: Message):
    title = await play_next(m.chat.id)
    if title:
        await m.reply(f"⏭️ Skip karke baj raha hai:\n{title}")
    else:
        await m.reply("Queue khali hai")

@app.on_message(filters.command("stop"))
async def stop(_, m: Message):
    chat_id = m.chat.id
    queue[chat_id] = []
    await call.leave_group_call(chat_id)
    await m.reply("⏹️ Band kar diya, VC se nikal gaya")

@app.on_message(filters.command("queue"))
async def show_queue(_, m: Message):
    q = queue.get(m.chat.id, [])
    if not q:
        return await m.reply("Queue khali hai")
    text = "🎶 **Queue:**\n\n"
    for i, (title, _, _) in enumerate(q, 1):
        text += f"{i}. {title}\n"
    await m.reply(text)

async def main():
    await app.start()
    await call.start()
    print("Blublu Bot Chal Gaya!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
