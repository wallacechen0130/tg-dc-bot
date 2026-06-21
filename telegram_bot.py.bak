import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

class TelegramBot:
    def __init__(self, token: str, channel_id: int):
        self.token = token
        self.channel_id = channel_id
        self.photo_file_ids = []
        self.app = ApplicationBuilder().token(self.token).build()
        photo_handler = MessageHandler(filters.Chat(self.channel_id) & filters.PHOTO, self.handle_photo)
        self.app.add_handler(photo_handler)

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message and update.message.photo:
            file_id = update.message.photo[-1].file_id
            self.photo_file_ids.append(file_id)
            if len(self.photo_file_ids) > 2000:
                self.photo_file_ids = self.photo_file_ids[-2000:]

    async def start(self):
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

    async def stop(self):
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

    async def get_random_photo_bytes(self) -> bytes | None:
        import random, io
        if not self.photo_file_ids:
            return None
        file_id = random.choice(self.photo_file_ids)
        bot = self.app.bot
        try:
            file = await bot.get_file(file_id)
            bio = io.BytesIO()
            await file.download_to_memory(out=bio)
            return bio.getvalue()
        except Exception as e:
            print(f'Failed to download telegram photo: {e}')
            return None
