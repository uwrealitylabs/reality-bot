import shutil

import discord
from discord import app_commands
from discord.ext import commands
from pathlib import Path

from modules.jlc2kicad_wrapper import *

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='$')
active_commands = set()

UWRL_GUILD_ID: int = 1181690091853328455


def _get_token():
    with open(Path("secret/token.txt"), 'r') as f:
        return f.read().strip()


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    guild = discord.Object(id=UWRL_GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)



# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
#
#     msg: str = message.content.lower()
#     if msg.startswith("$jlc") or msg.startswith("$jlc2kicad"):
#         await message.channel.send('Hello!')


@bot.hybrid_command(name="jlc2kicad", description="Generate a component library for KiCad from the "
                                                       "JLCPCB/easyEDA library")
@app_commands.describe(parts="JLCPCB part numbers, separated by whitespace")
async def jlc2kicad(ctx, *, parts: str):
    print("received")
    out_dir = Path("output")
    jlc_to_kicad(list(parts.split()), out_dir)

    zip_path = Path("kicad_lib.zip")
    if zip_path.exists():
        zip_path.unlink()
    shutil.make_archive(zip_path.stem, 'zip', out_dir)

    result_file = discord.File(zip_path)
    await ctx.send(file=result_file)


@jlc2kicad.error
async def jlc2kicad_error(ctx, error):
    await ctx.send("ERROR")
    raise error


bot.run(_get_token())
