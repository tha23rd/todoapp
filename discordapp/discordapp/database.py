from typing import Any
from typing import Dict
from typing import Union

import aiohttp
import discord.ext.commands
from discord import Color
from discord import Embed
from discord.ext import commands
from discord_slash import ComponentContext
from discord_slash import SlashContext
from discord_slash import cog_ext
from discord_slash.utils.manage_components import create_actionrow
from discord_slash.utils.manage_components import create_button

# Be sure to update this to be able to update commands instantly
guild_ids = [532850691019112478]
api_url = "http://f0dc6ae37f49.ngrok.io/todolist"
user_url = "http://pumped-dogs.surge.sh/#/todo/"


async def post_request() -> Dict[str, str]:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/") as resp:
            response = await resp.json()
            return response


async def get_request(
    list_id: str,
) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_url}/{list_id}") as resp:
            response = await resp.json()
            return response


def parse_response(response: Dict[str, Any]) -> str:
    if "items" in response and "id" in response:
        items = response["items"]
        parsed_items = f"**{response['name']}**\n"  # - id: {response['id']}
        for item in items:
            parsed_items += f"{item['name']:<25}{get_emoji(item['is_complete'])}\n"
        return parsed_items if parsed_items else "empty_list"
    else:
        raise Exception(response)


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
        if "detail" in response:
            await self.view_error(ctx, response["detail"])
            return
        else:
            parsed_response = parse_response(response)
            buttons = [
                create_button(
                    style=1,
                    emoji="🔄",
                    custom_id="refresh_list",
                    label=f"{todo_list_id}",
                ),
                create_button(
                    style=5, label="View List", url=f"{user_url}/{todo_list_id}"
                ),
            ]
            action_row = create_actionrow(*buttons)
            await ctx.send(parsed_response, components=[action_row])

    @cog_ext.cog_component(components="refresh_list")
    async def refresh_list(self, ctx: ComponentContext) -> None:
        list_id = ctx.component["label"]
        response = await get_request(list_id)
        if "detail" in response:
            parsed_response = response["detail"]
        else:
            parsed_response = parse_response(response)
        await ctx.edit_origin(content=parsed_response)

    @view_todolist.error
    async def view_error(self, ctx: SlashContext, error: str) -> None:
        embed = Embed(title="View Error", color=Color.red(), description=error)
        await ctx.send(embed=embed)
        print(error)


def setup(bot: discord.ext.commands.bot.Bot) -> None:
    bot.add_cog(Database(bot))
