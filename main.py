import os
import asyncio
from dotenv import load_dotenv
from telegram_bot import TelegramBot
from discord_bot import setup_discord

load_dotenv()

async def main():
    tg_token = os.getenv('TG_TOKEN')
    tg_channel_id = int(os.getenv('TG_CHANNEL_ID'))
    dc_token = os.getenv('DC_TOKEN')

    tg_bot = TelegramBot(tg_token, tg_channel_id)
    await tg_bot.start()

    await setup_discord(dc_token, tg_bot)

if __name__ == '__main__':
    asyncio.run(main())

    #py -3.13 "c:\claude_projects\TG-DC bot\main.py"