import random

import discord

from src import input_validation as inval
from src import logic
from src import log
from src import db, bot
from src.constants import SHAXX_QUOTES, OW_HEROS
from src.bungie.models import BungieUser


@bot.command()
async def golden_gun(ctx):
    """
    Choose the next Overwatch Golden Gun for you to get.
    For Example:
            "golden_gun 1 8 15 24 28"
            Where the numbers are the heros who you already have golden guns
            for. Try "heros" for hero-number pairs
    """
    owned_heros, err = inval.golden_gun(ctx.message.content, ctx.message.author)
    if err is not None:
        return await ctx.message.channel.send(err)
    return await ctx.message.channel.send(
        f"{ctx.message.author.mention} your next golden gun is for {logic.golden_gun(owned_heros)}"
    )


@bot.command(pass_context=True)
async def quote(ctx):
    quotes_channel = discord.utils.get(ctx.guild.channels, name="quotes")
    quotes = []
    async for q in discord.iterators.HistoryIterator(quotes_channel, 100):
        quotes.append(q)
    return await ctx.message.channel.send(logic.quote(quotes))


@bot.command(pass_context=True)
async def random_num(ctx):
    """
    Gets a Random integer between 0 and given max
    For example:
            "random_number 3"
            will return a 0, 1, 2, or 3
    """
    nums, err = inval.random_num(ctx.message.content)
    if err is not None:
        return await ctx.message.channel.send(err)
    lower, upper = nums
    return await ctx.message.channel.send(logic.random_num(lower, upper))


@bot.command(pass_context=True)
async def roles(ctx):
    """
    Displays Your current roles as well as the currently toggleable roles
    """
    return await ctx.message.channel.send(
        "{}:\n{}".format(ctx.message.author.mention, logic.roles(ctx.message))
    )


@bot.command(pass_context=True)
async def toggle_role(ctx):
    """
    Toggles given role on or off
    for example:
            "toggle_role overwatch"
            will add or remove the overwatch role
    Try "roles" for Currently Toggleable Roles
    """
    # gets toggleable Roles
    roles, err = inval.toggle_role(ctx.message.content, ctx.message.channel)
    if err is not None:
        return await ctx.message.channel.send(err)
    msg = await logic.toggle_role(ctx.message.author, roles)
    return await ctx.message.channel.send(msg)


@bot.command(pass_context=True)
async def hello(ctx):
    """
    Says Hello to whomever called it
    """
    msg = "Hi {0.author.mention}".format(ctx.message)
    await ctx.message.channel.send(msg)


@bot.command(pass_context=True)
async def heros(ctx):
    msg = ""
    for k in OW_HEROS:
        msg += "{}: {}\n".format(k, OW_HEROS[k])
    await ctx.message.channel.send(msg)


@bot.command(pass_context=True)
async def shaxx(ctx):
    # join the VC
    vc = None
    try:
        voice_channel = ctx.message.author.voice.channel
        vc = await voice_channel.connect()
    except discord.errors.ClientException:
        await ctx.message.channel.send("LET ME FINISH!")
    except AttributeError:
        pass  # User is not in a VC
    finally:
        await ctx.message.channel.send(f"{random.choice(SHAXX_QUOTES)}")
        if vc:
            await vc.disconnect()


@bot.command(pass_context=True)
async def thanks(ctx):
    await ctx.message.channel.send(
        "You're Welcome {}!".format(ctx.message.author.mention)
    )


@bot.command()
async def echo(ctx):
    return await ctx.message.channel.send(
        ctx.message.content.removeprefix(f"{ctx.bot.command_prefix}echo")
    )


@bot.command()
async def cs(ctx):
    dir_ = logic.cs()
    log.info(f"`cs` was called, {dir_} returned")
    return await ctx.message.channel.send(file=discord.File(dir_))


@bot.command()
async def register(ctx):
    # Check DB to see if User is already registered.
    if user := db.get(ctx.message.author.id) is not None:
        return await ctx.message.author.send("You are already registered.")
    await ctx.message.channel.send(
        "Check your direct messages for Destiny Registration info."
    )

    async def prompt(message):
        await ctx.author.send(message)
        response = await bot.wait_for(
            "message", check=lambda msg: msg.author == ctx.author
        )
        return response.content

    code = await BungieUser._get_user_code(prompt=prompt)
    token = BungieUser._get_auth_token(code)
    user = BungieUser.init_from_auth_token(token, ctx.author.id)
    user.save_to_db()
    return await ctx.author.send("You are now registered")
