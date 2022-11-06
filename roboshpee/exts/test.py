"""
A file to test stuff, should not be expected to work.
"""

from discord.ext import commands

from roboshpee.bot import Bot
from roboshpee.constants import MASTER_SHPEE
from roboshpee.menu import ReactionMenu, ReactionMenuOption
from roboshpee.security import requires_exact_role


@commands.group()
async def test(ctx):
    if ctx.invoked_subcommand is not None:
        return


@test.command()
@requires_exact_role(MASTER_SHPEE)
async def menu(ctx):
    msg = await ctx.send("Creating menu...")
    options = {
        "🐟": ReactionMenuOption(callback_func=lambda: print("🐟 - Option 1 Callback")),
        "✅": ReactionMenuOption(callback_func=lambda: print("✅ - Option 2 Callback")),
        "❌": ReactionMenuOption(callback_func=lambda: print("❌ - Option 3 Callback")),
    }
    menu = await ReactionMenu.create(ctx, msg, "This is a test message", options)
    await menu.wait_for_results()


async def setup(bot: Bot) -> None:
    bot.add_command(test)
