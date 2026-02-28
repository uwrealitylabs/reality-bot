import discord
from discord import app_commands
from discord.ext import commands

from modules.jlc2kicad_wrapper import *

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='$')
active_commands = set()

UWRL_GUILD_ID: int = 1181690091853328455
LOG_CHANNEL_ID: int = 1417347796628934707


def _get_token():
    with open(Path("secret/token.txt"), 'r') as f:
        return f.read().strip()


async def _get_log_channel():
    return await bot.fetch_channel(LOG_CHANNEL_ID)


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
    await ctx.send("Generating KiCad component library...")
    out_dir = Path("temp/output")
    if not jlc_to_kicad(list(parts.split()), out_dir) or not out_dir.exists():
        await ctx.send("Failed to create component library, your part number is likely wrong.")
        return

    zip_path = Path("temp/kicad_lib.zip")
    if zip_path.exists():
        zip_path.unlink()
    shutil.make_archive(str(zip_path.with_suffix("")), 'zip', out_dir)

    result_file = discord.File(zip_path)
    await ctx.send("Success! Result attached.", file=result_file)


@jlc2kicad.error
async def jlc2kicad_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Usage: `$jlc2kicad part1 [part2 part3 ...]`")
        return
    await ctx.send(f"Unexpected error encountered. Details printed to <#{LOG_CHANNEL_ID}>")
    log_channel = await _get_log_channel()
    await log_channel.send(f"`{str(error)}`")
    raise error


if __name__ == "__main__":
    bot.run(_get_token())
