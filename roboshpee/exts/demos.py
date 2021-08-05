import discord
from discord.ext import commands

from roboshpee.bot import Bot
from roboshpee.constants import PREFIX
from roboshpee.utils import ReactionMenu, ReactionMenuOption


@commands.group()
async def demo(ctx):
    """
    A group of demonstrations and proof of concepts.
    """
    if ctx.invoked_subcommand is not None:
        return
    await ctx.send(f"See `{PREFIX}help demo` for more info.")


@demo.command()
async def embeded_menu(ctx):
    """
    Demo of a dynamic reaction biased menu system.
    In this case used to vote on the best animal.
        (Phil only needs one vote to win though...)
    """
    fish_name = "Fred the Fish - 🐟"
    dog_name = "Dan the Dog - 🐶"
    pig_name = "Phil the Pig - 🐷"

    # Create the embeded object that we want to modify later.
    # We don't have to use a embed, but it makes it easier to modify piecewise.
    embed = discord.Embed(
        title="Animal Poll", description="Vote for your favorite Animal"
    )
    embed.insert_field_at(index=0, name=fish_name, value="No Votes yet.")
    embed.insert_field_at(index=1, name=dog_name, value="No Votes yet.")
    embed.insert_field_at(index=2, name=pig_name, value="No Votes yet.")

    # This wraps the needed state into the function scope so it
    # can be accessed later. The inner function can be asynchronous or synchronous,
    # but it will always have the ReactionMenuOption that it is attached
    # to passed to it
    def on_reaction_add(embed, embed_idx, msg, name: str, value: str):
        async def wrapped(self: ReactionMenuOption):
            embed.set_field_at(
                index=embed_idx, name=name, value=value.format(self.state)
            )
            await msg.edit(embed=embed)

        return wrapped

    msg = await ctx.send(embed=embed)

    fish_on_update_hook = on_reaction_add(
        embed, 0, msg, name=fish_name, value="Fred has {} Votes!"
    )
    dog_on_update_hook = on_reaction_add(
        embed, 1, msg, name=dog_name, value="Dan has {} Votes!"
    )
    pig_on_update_hook = on_reaction_add(
        embed, 2, msg, name=pig_name, value="Phil has {} Votes!"
    )

    def generate_callback_func(embed, embed_idx, msg, name, value):
        async def wrapped():
            embed.set_field_at(index=embed_idx, name=name, value=value)
            await msg.edit(embed=embed)

        return wrapped

    fish_callback = generate_callback_func(embed, 0, msg, fish_name, "✨✨ Fred Won! ✨✨")
    dog_callback = generate_callback_func(embed, 1, msg, dog_name, "✨✨ Dan Won! ✨✨")
    pig_callback = generate_callback_func(embed, 2, msg, pig_name, "✨✨ Phil Won! ✨✨")

    options = {
        "🐟": ReactionMenuOption(
            callback_func=fish_callback,
            on_reaction_add=fish_on_update_hook,
            on_reaction_remove=fish_on_update_hook,
            callback_trigger=10,
        ),
        "🐶": ReactionMenuOption(
            callback_func=dog_callback,
            on_reaction_add=dog_on_update_hook,
            on_reaction_remove=dog_on_update_hook,
            callback_trigger=10,
        ),
        "🐷": ReactionMenuOption(
            callback_func=pig_callback,
            on_reaction_add=pig_on_update_hook,
            on_reaction_remove=pig_on_update_hook,
            callback_trigger=1,
        ),
    }
    menu = await ReactionMenu.create(ctx, msg, "", options)
    await menu.wait_for_results()


def setup(bot: Bot) -> None:
    bot.add_command(demo)
