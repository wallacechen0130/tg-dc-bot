import discord
import io
from discord.ext import commands
from telegram_bot import TelegramBot


class DiscordBot(commands.Cog):
    def __init__(self, bot: commands.Bot, tg_bot: TelegramBot):
        self.bot = bot
        self.tg_bot = tg_bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.strip() == '!瑟圖':
            data = await self.tg_bot.get_random_photo_bytes()

            if not data:
                await message.channel.send('沒有可用的圖片。')
                return

            file = discord.File(io.BytesIO(data), filename='image.jpg')
            await message.channel.send(file=file)


async def setup_discord(bot_token: str, tg_bot: TelegramBot):
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    await bot.add_cog(DiscordBot(bot, tg_bot))

    await bot.start(bot_token)