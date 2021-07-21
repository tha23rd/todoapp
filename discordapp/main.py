# Not leaving token in plaintext because public repo
import logging

from discord.ext import commands
from discord_slash import SlashCommand
from tokens import token

client = commands.Bot(command_prefix="/", case_insensitive=True)
slash = SlashCommand(client, sync_commands=True)

logger = logging.getLogger("discord")
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


@client.event
async def on_ready() -> None:
    print("Connected to Discord!")


client.load_extension("database")

client.run(token)
