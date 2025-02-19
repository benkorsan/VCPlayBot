

from asyncio import QueueEmpty
from pyrogram import Client 
from pyrogram import filters
from pyrogram.types import Message

from VCPlayBot.config import que
from VCPlayBot.function.admins import set
from VCPlayBot.helpers.channelmusic import get_chat_id
from VCPlayBot.helpers.decorators import authorized_users_only
from VCPlayBot.helpers.decorators import errors
from VCPlayBot.helpers.filters import command
from VCPlayBot.helpers.filters import other_filters
from VCPlayBot.services.callsmusic import callsmusic
from VCPlayBot.services.queues import queues


@Client.on_message(filters.command("reload"))
async def update_admin(client, message: Message):
    chat_id = get_chat_id(message.chat)
    set(
        chat_id,
        [
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("🕊️ Yönetici önbelleği yenilendi✅!")


@Client.on_message(command("pause") & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.active_chats) or (
        callsmusic.active_chats[chat_id] == "paused"
    ):
        await message.reply_text("❗ Hiçbir şey oynamıyor!")
    else:
        callsmusic.pause(chat_id)
        await message.reply_text("▶️ Duraklatıldı!")


@Client.on_message(command("resume") & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.active_chats) or (
        callsmusic.active_chats[chat_id] == "playing"
    ):
        await message.reply_text("❗ Hiçbir şey duraklatılmaz!")
    else:
        callsmusic.resume(chat_id)
        await message.reply_text("⏸ Devam!")


@Client.on_message(command("son") & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.active_chats:
        await message.reply_text("❗ Hiçbir şey yayınlanmıyor!")
    else:
        try:
            queues.clear(chat_id)
        except QueueEmpty:
            pass

        await callsmusic.stop(chat_id)
        await message.reply_text("❌ Yayın durduruldu!")


@Client.on_message(command("skip") & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.active_chats:
        await message.reply_text("❗ Atlamak için hiçbir şey oynamıyor!")
    else:
        queues.task_done(chat_id)
        if queues.is_empty(chat_id):
            await callsmusic.stop(chat_id)
        else:
            await callsmusic.set_stream(
                chat_id, 
                queues.get(chat_id)["file_path"]
            )

    qeue = que.get(chat_id)
    if qeue:
        skip = qeue.pop(0)
    if not qeue:
        return
    await message.reply_text(f"- Atlanır **{skip[0]}**\n- Şimdi Çalınıyor **{qeue[0][0]}**")


@Client.on_message(filters.command("admincache"))
@errors
async def admincache(client, message: Message):
    set(
        message.chat.id,
        [
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ],
    )
    await message.reply_text("❇️ Yönetici önbelleği yenilendi!")
