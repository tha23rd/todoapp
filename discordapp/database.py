from typing import Any
from typing import Dict
from typing import Union

import aiohttp
import discord.ext.commands
from discord import Color
from discord import Embed
from discord.ext import commands
from discord_slash import SlashContext
from discord_slash import cog_ext

# Be sure to update this to be able to update commands instantly
guild_ids = [532850691019112478]
url = "http://127.0.0.1:8000/todolist"


async def post_request() -> Dict[str, str]:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{url}/") as resp:
            response = await resp.json()
            return response


async def get_request(
    list_id: str,
) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/{list_id}") as resp:
            response = await resp.json()
            return response


def get_emoji(completed: Union[str, bool]) -> str:
    if completed:
        return ":green_circle:"
    else:
        return ":red_circle:"


class Database(commands.Cog):
    def __init__(self, bot: discord.ext.commands.bot.Bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="create", description="Create a new todo list", guild_ids=guild_ids
    )
    async def create_todolist(self, ctx: SlashContext) -> None:
        response = await post_request()
        if "id" in response:
            embed = Embed(title=f"Created list: {response['id']}", color=Color.green())
            await ctx.send(embed=embed)
        elif "detail" in response:
            await self.view_error(ctx, response["detail"])
        else:
            raise Exception(response)

    @cog_ext.cog_slash(
        name="view", description="View a specified todo list", guild_ids=guild_ids
    )
    async def view_todolist(self, ctx: SlashContext, todo_list_id: str) -> None:
        response = await get_request(todo_list_id)
        if "name" in response:
            items = response["items"]
            # embed = Embed(title=f"{response['name']}", color=Color.blue(), description=todo_list_id)
            parsed_items = f"**{response['name']}** - id: {todo_list_id}\n"
            for item in items:
                parsed_items += f"{item['name']:<25}{get_emoji(item['is_complete'])}\n"
            # embed.add_field(name="Items", value=parsed_items if parsed_items else "empty_list")
            await ctx.send(parsed_items if parsed_items else "empty_list")
        elif "detail" in response:
            await self.view_error(ctx, response["detail"])
        else:
            raise Exception(response)

    @view_todolist.error
    async def view_error(self, ctx: SlashContext, error: str) -> None:
        embed = Embed(title="View Error", color=Color.red(), description=error)
        await ctx.send(embed=embed)
        print(error)


def setup(bot: discord.ext.commands.bot.Bot) -> None:
    bot.add_cog(Database(bot))
