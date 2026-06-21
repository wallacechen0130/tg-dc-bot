"""
姝峰彶鐓х墖瑁滄姄妯＄祫銆�

鐢� Telethon锛堝€嬩汉甯宠櫉锛夐€ｇ窔鍒版寚瀹氶牷閬擄紝寰炴渶鏂板線鍥炴姄鐓х墖瑷婃伅锛�
鎶婂湒鐗囧収瀹瑰瓨鎴愭湰鍦版獢妗堬紝鏁搁噺涓婇檺鐢� MAX_PHOTOS 鎺у埗銆�

绗竴娆″煼琛岄渶瑕佷簰鍕曞紡杓稿叆鎵嬫椹楄瓑纰硷紙Telegram app 鏀跺埌鐨勯璀夌⒓锛�
涓嶆槸绨¤▕锛夛紝鐧诲叆鎴愬姛寰屾渻鍦ㄦ湰鍦扮敘鐢熶竴鍊� .session 妾旀锛�
涔嬪緦鍩疯锛堝寘鎷 main.py 鑷嫊鍛煎彨鏅傦級灏变笉闇€瑕佸啀娆¤几鍏ラ璀夌⒓銆�

鐛ㄧ珛鍩疯锛堝缓璀扮涓€娆″厛鎵嬪嫊璺戦€欏€嬶紝瀹屾垚鐧诲叆锛夛細
    python backfill.py

鎴栬 main.py 鍦ㄥ暉鍕曟檪鑷嫊鍛煎彨 run_backfill()銆�
"""

import os
import asyncio
import shutil
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from telethon.network.connection.tcpobfuscated import ConnectionTcpObfuscated

load_dotenv()

API_ID = int(os.getenv('TG_api_id'))
API_HASH = os.getenv('TG_api_hash')

SESSION_NAME = 'backfill_session'  # 鏈冪敘鐢� backfill_session.session 妾旀
PHOTO_DIR = Path('photo_cache')    # 鍦栫墖瀛樻斁璩囨枡澶�
MAX_PHOTOS = 1500                  # 鎶撳彇涓婇檺


async def run_backfill(channel_id: int):
    """娓呯┖鑸婂揩鍙栵紝閲嶆柊寰為牷閬撴姄鍙栨渶鏂� MAX_PHOTOS 寮电収鐗囧瓨鍒版湰鍦般€�"""

    # 鍟熷嫊鏅傚厛娓呯┖鑸婅硣鏂欏ぞ锛岀⒑淇濆彧鐣欎笅閫欐鎶撳埌鐨勫収瀹�
    if PHOTO_DIR.exists():
        shutil.rmtree(PHOTO_DIR)
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)

    # 閮ㄥ垎涓绘鐠板鐨勯槻鐏墕鏈冪敤 DPI 鍋垫脯涓﹂樆鏂锋婧� MTProto 灏佸寘鏍煎紡锛�
    # 鏀圭敤 Obfuscated 閫ｇ窔妯″紡锛屾妸娴侀噺鍋借鎴愰毃姗熻硣鏂欎互绻為亷鍋垫脯
    client = TelegramClient(
        SESSION_NAME, API_ID, API_HASH,
        connection=ConnectionTcpObfuscated,
        connection_retries=3,
        timeout=15,
    )
    await client.start()  # 宸叉湁 session 妾旀鏅備笉鏈冭姹傝几鍏ラ璀夌⒓

    saved_count = 0
    print(f'闁嬪寰為牷閬撴姄鍙栨鍙茬収鐗囷紝涓婇檺 {MAX_PHOTOS} 寮�...')

    async for message in client.iter_messages(channel_id):
        if saved_count >= MAX_PHOTOS:
            break

        if message.media and isinstance(message.media, MessageMediaPhoto):
            file_path = PHOTO_DIR / f'{message.id}.jpg'
            try:
                await client.download_media(message, file=str(file_path))
                saved_count += 1
                if saved_count % 100 == 0:
                    print(f'宸叉姄鍙� {saved_count} 寮�...')
            except Exception as e:
                print(f'涓嬭級瑷婃伅 {message.id} 澶辨晽: {e}')
                continue

    print(f'瀹屾垚锛屽叡鎶撳彇 {saved_count} 寮电収鐗囷紝瀛樻斁鏂� {PHOTO_DIR.resolve()}')
    await client.disconnect()


if __name__ == '__main__':
    channel_id = int(os.getenv('TG_CHANNEL_ID'))
    asyncio.run(run_backfill(channel_id))

