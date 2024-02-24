import asyncio

import asyncpg
import discord
from discord.ext import commands
from yoyo import read_migrations, get_backend

import common.constant
from common import util
from common.util import logger, config, installation_path
from dao.context_free_dao import insert_bot_version_if_not_present
from service.chatbot_service import ChatbotService

dbUrl = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
    config.get_str('database', 'username'),
    config.get_str('database', 'password'),
    config.get_str('database', 'host'),
    config.get_str('database', 'port'),
    config.get_str('database', 'database')
)

backend = get_backend(dbUrl)
migrations = read_migrations(f'{installation_path}/db')

with backend.lock():
    backend.apply_migrations(backend.to_apply(migrations))

intents = discord.Intents.all()
bot = commands.Bot(common.constant.COMMAND_MARKER, intents=intents)


async def run():
    credentials = {
        "user": config.get_str('database', 'username'),
        "password": config.get_str('database', 'password'),
        "host": config.get_str('database', 'host'),
        "port": config.get_str('database', 'port'),
        "database": config.get_str('database', 'database')
    }

    async with asyncpg.create_pool(**credentials) as pool:
        async with pool.acquire() as conn:
            await insert_bot_version_if_not_present(common.util.version, conn)

        chatbot_service = ChatbotService(bot, pool)

        @bot.event
        async def on_ready():
            logger.info(f'{bot.user} has connected to Discord!')

        @bot.event
        async def on_message(message: discord.Message):
            if message.author.id != bot.user.id and message.channel != message.author.dm_channel:
                return
            if not message.content.startswith(common.constant.COMMAND_MARKER):
                await chatbot_service.handle_new_message(message)
            await bot.process_commands(message)

        @bot.command()
        async def reset(ctx: discord.ext.commands.Context):
            await chatbot_service.handle_command_reset(ctx)

        @bot.command()
        async def version(ctx: discord.ext.commands.Context):
            await chatbot_service.handle_command_version(ctx)

        @bot.command()
        async def fast(ctx: discord.ext.commands.Context):
            await chatbot_service.handle_command_speed(ctx, 0.01)

        @bot.command()
        async def slow(ctx: discord.ext.commands.Context):
            await chatbot_service.handle_command_speed(ctx, 1)

        @bot.command()
        async def debug(ctx: discord.ext.commands.Context):
            await chatbot_service.handle_command_debug(ctx, None)

        @bot.command()
        async def debugon(ctx: discord.ext.commands.Context):
            await chatbot_service.handle_command_debug(ctx, True)

        @bot.command()
        async def debugoff(ctx: discord.ext.commands.Context):
            await chatbot_service.handle_command_debug(ctx, False)

        @bot.command()
        async def acks(ctx: discord.ext.commands.Context):
            await chatbot_service.handle_command_acks(ctx)

        @bot.command()
        async def report(ctx: discord.ext.commands.Context):
            await chatbot_service.handle_command_report(ctx)

        await bot.start(config.get_str('discord', 'token'))


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(run())
except KeyboardInterrupt:
    loop.run_until_complete(bot.close())
