from pyrogram.types import Chat


def get_chat_id(chat: Chat):
    if chat.title.startswith("Kanal Müzik: ") and chat.title[16:].isnumeric():
        return int(chat.title[15:])
    return chat.id
