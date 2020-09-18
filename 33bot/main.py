import discord
import logging
import asyncio
import os
import random
from Exceptions import ZerothHeroError, TooManyHerosError
from discord.ext import commands
from constants import PREFIX, OVERWATCH_HEROS, SHAXX_QUOTES

# get TOKEN
TOKEN = os.environ["DISCORD_TOKEN"]


# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("33bot.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Set up discord bot
bot = commands.Bot(command_prefix=PREFIX)


@bot.event
async def on_ready():
    print("Logged in as:")
    print(bot.user.name)
    print(bot.user.id)
    print("--------------\n\n")


# set up opus to use voice
# discord.opus.load_opus('libopus-0.x86.dll')


# Commands ---------------------------------
@bot.command(pass_context=True)
async def golden_gun(ctx):
    """
    Choose the next Overwatch Golden Gun for you to get.
    For Example:
            "golden_gun 1 8 15 24 28"
            Where the numbers are the heros who you already have golden guns for
            Try "heros" for hero-number pairs
    """
    try:
        owned = set([abs(int(x)) for x in ctx.message.content.split()[1:]])
        if len(owned) > len(OVERWATCH_HEROS):
            raise TooManyHerosError
        if 0 in owned:
            raise ZerothHeroError
    except ValueError:
        return await ctx.message.channel.send(
            "{}, arguments must be numeric,"
            " try 'heros' for a list of hero-number pairs".format(
                ctx.message.author.mention
            )
        )
    except TooManyHerosError:
        return await ctx.message.channel.send(
            "{}, No, BOB still isn't a playable hero :(\t"
            "*(if more heros have been added let KGB know to update his list)*".format(
                ctx.message.author.mention
            )
        )
    except ZerothHeroError:
        return await ctx.message.channel.send(
            "{}, There isn't a Zeroth Hero".format(ctx.message.author.mention)
        )
    try:
        return await ctx.message.channel.send(
            "{}, Your next Golden Gun is for {}!".format(
                ctx.message.author.mention,
                OVERWATCH_HEROS[random.choice(list((OVERWATCH_HEROS.keys() ^ owned)))],
            )
        )
    except IndexError:
        return await ctx.message.channel.send(
            "{} is a liar!, They dont have every golden gun!".format(
                ctx.message.author.mention
            )
        )


@bot.command(pass_context=True)
async def quote(ctx):
    quotes_channel = discord.utils.get(bot.get_all_channels(), name="quotes")
    quotes = []
    async for q in discord.iterators.HistoryIterator(quotes_channel, 100):
        quotes.append(q)
    return await ctx.message.channel.send(random.choice(quotes).content)


@bot.command(pass_context=True)
async def random_num(ctx):
    """
    Gets a Random integer between 0 and given max
    For example:
            "random_number 3"
            will return a 0, 1, 2, or 3
    """
    rand_num = None
    try:
        max_num = int(ctx.message.content.split()[1])
    except ValueError:  # Max num isn't an int
        return await ctx.message.channel.send(
            "{}, '{}' isn't a number dummy".format(
                ctx.message.author.mention, ctx.message.content.split()[1]
            )
        )
    try:
        rand_num = random.randint(0, max_num)
    except ValueError:  # Max num is negative
        rand_num = random.randint(max_num, 0)
    finally:
        return await ctx.message.channel.send(
            "{},\tYour random number (between 0 and {}) is: {}".format(
                ctx.message.author.mention, max_num, rand_num
            )
        )


@bot.command(pass_context=True)
async def roles(ctx):
    """
    Displays Your current roles as well as the currently toggleable roles
    """
    current_roles = [r.name for r in reversed(ctx.message.author.roles)][:-1]
    your_toggleable_roles = []
    toggleable_roles = []

    for role in ctx.message.channel.guild.roles:
        if str(role.color) == "#206694":
            toggleable_roles += [
                role,
            ]
    toggleable_roles.sort()

    for r in reversed(toggleable_roles):
        if r in current_roles:
            your_toggleable_roles += [
                "**" + r.name.strip() + "**",
            ]
        else:
            your_toggleable_roles += [
                r.name,
            ]

    msg = "Your Current Roles: {}\nToggleable Roles: {}".format(
        current_roles, your_toggleable_roles
    )
    return await ctx.message.channel.send(
        "{}:\n{}".format(ctx.message.author.mention, msg)
    )


@bot.command(pass_context=True)
async def spam(ctx):
    """
    Spams the person mentioned
    ex: spam @player 10
    will mention player 10 times
    """
    if ctx.message.channel.name.lower() == "spam":
        num = int(ctx.message.content.split()[-1])
        for _ in range(num):
            await ctx.message.channel.send(ctx.message.author.mention)
            await asyncio.sleep(random.randint(0, 120))
    else:
        return await ctx.message.channel.send(
            "This Command can only be called in the '#spam' channel"
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
    toggleable_roles = []
    for role in ctx.message.channel.guild.roles:
        if str(role.color) == "#206694":
            toggleable_roles += [
                role.name,
            ]

    try:
        role_to_toggle = ctx.message.content.split()[1]

        if (
            role_to_toggle in toggleable_roles
        ):  # Checks to See if given role is toggleable
            role_to_toggle = discord.utils.get(
                ctx.message.channel.guild.roles, name=role_to_toggle
            )

            # Toggle role
            if role_to_toggle in ctx.message.author.roles:  # Removes Role
                await ctx.message.author.remove_roles(role_to_toggle)
                await ctx.message.channel.send(
                    "{}: Role removed".format(ctx.message.author.mention)
                )
            else:  # Gives Role
                await ctx.message.author.add_roles(role_to_toggle)
                await ctx.message.channel.send(
                    "{}: Role Added".format(ctx.message.author.mention)
                )

        # Role is not toggleable
        else:
            await ctx.message.channel.send(
                'Role Not Found, try "{}roles" for a list of toggleable roles'.format(
                    PREFIX
                )
            )

    # Checks to see if a role was given
    except IndexError:
        await ctx.message.channel.send(
            'You must add a valid role, try "{}help" for help'.format(PREFIX)
        )


# Hidden Commands ---------------------------


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
    for k in OVERWATCH_HEROS:
        msg += "{}: {}\n".format(k, OVERWATCH_HEROS[k])
    await ctx.message.channel.send(msg)


@bot.command(pass_context=True)
async def rtd(ctx):
    await ctx.message.channel.send("Nothing's Here. Any Suggestions?")


@bot.command(pass_context=True)
async def shaxx(ctx):
    # join the VC
    vc = None
    try:
        voice_channel = ctx.message.author.voice.channel
        vc = await voice_channel.connect()
    except discord.errors.ClientException:  # Raised if the bot is already in a channel
        await ctx.message.channel.send("LET ME FINISH!")
    except AttributeError:  # User is not in a VC
        pass
    # Play the shaxx quote
    finally:
        await ctx.message.channel.send("{}".format(random.choice(SHAXX_QUOTES)))
        await vc.disconnect()


@bot.command(pass_context=True)
async def thanks(ctx):
    await ctx.message.channel.send(
        "You're Welcome {}!".format(ctx.message.author.mention)
    )


if __name__ == "__main__":
    bot.run(TOKEN)
