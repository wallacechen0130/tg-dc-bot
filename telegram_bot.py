import os
import random
from pathlib import Path

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

PHOTO_DIR = Path('photo_cache')
MAX_CACHED_PHOTOS = 1500


class TelegramBot:
    def __init__(self, token: str, channel_id: int):
        self.token = token
        self.channel_id = channel_id
        self.app = ApplicationBuilder().token(self.token).build()

        PHOTO_DIR.mkdir(parents=True, exist_ok=True)

        # 記憶體只存檔名清單（字串），不存圖片內容本身
        self.photo_filenames: list[str] = self._load_existing_filenames()

        photo_handler = MessageHandler(filters.Chat(self.channel_id) & filters.PHOTO, self.handle_photo)
        self.app.add_handler(photo_handler)

    def _load_existing_filenames(self) -> list[str]:
        """啟動時掃描 photo_cache 資料夾，把已有檔名載入記憶體清單。
        (backfill.py 抓到的歷史照片，以及上次運行期間累積的新照片都在這裡)"""
        if not PHOTO_DIR.exists():
            return []
        filenames = [f.name for f in PHOTO_DIR.iterdir() if f.is_file()]
        print(f'已載入 {len(filenames)} 張本地快取照片的檔名清單。')
        return filenames

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message and update.message.photo:
            photo = update.message.photo[-1]
            file_id = photo.file_id
            filename = f'{update.message.id}.jpg'
            file_path = PHOTO_DIR / filename

            try:
                file = await context.bot.get_file(file_id)
                await file.download_to_drive(custom_path=str(file_path))
            except Exception as e:
                print(f'下載新照片失敗: {e}')
                return

            self.photo_filenames.append(filename)

            # 超過上限時，移除最舊的檔案(清單最前面)，避免硬碟空間無限增長
            while len(self.photo_filenames) > MAX_CACHED_PHOTOS:
                oldest = self.photo_filenames.pop(0)
                oldest_path = PHOTO_DIR / oldest
                if oldest_path.exists():
                    oldest_path.unlink()

    async def start(self):
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

    async def stop(self):
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

    async def get_random_photo_bytes(self) -> bytes | None:
        results = await self.get_random_photos_bytes(1)
        return results[0] if results else None

    async def get_random_photos_bytes(self, count: int) -> list[bytes]:
        if not self.photo_filenames or count <= 0:
            return []

        sample_size = min(count, len(self.photo_filenames))
        chosen_filenames = random.sample(self.photo_filenames, sample_size)

        results = []
        for filename in chosen_filenames:
            file_path = PHOTO_DIR / filename
            try:
                with open(file_path, 'rb') as f:
                    results.append(f.read())
            except Exception as e:
                print(f'讀取本地圖片失敗 {filename}: {e}')
                # 檔案可能已被刪除或損毀，從清單中移除避免重複出錯
                if filename in self.photo_filenames:
                    self.photo_filenames.remove(filename)
                continue

        return results
