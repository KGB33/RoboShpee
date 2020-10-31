import random

import discord
from discord.ext.commands import command

from src.constants import OW_HEROS, SHAXX_QUOTES
from src import BASE_DIR


@command(pass_context=True)
async def golden_gun(ctx):
    """
    Choose the next Overwatch Golden Gun for you to get.
    For Example:
            "golden_gun 1 8 15 24 28"
            Where the numbers are the heros who you already have golden guns
            for. Try "heros" for hero-number pairs
    """
    try:
        owned = set([abs(int(x)) for x in ctx.message.content.split()[1:]])
        if len(owned) > len(OW_HEROS):
            return await ctx.message.channel.send(
                f"{ctx.message.author.mention}, Either my list is out of date"
                "or you've entered too many heros."
            )
        if 0 in owned:
            return await ctx.message.channel.send(
                f"{ctx.message.author.mention}, There isn't a Zeroth Hero"
            )
    except ValueError:
        return await ctx.message.channel.send(
            "{}, arguments must be numeric,"
            " try 'heros' for a list of hero-number pairs".format(
                ctx.message.author.mention
            )
        )
    try:
        hero = OW_HEROS[random.choice(list((OW_HEROS.keys() ^ owned)))]
        return await ctx.message.channel.send(
            f"{ctx.message.author.mention}, Your next Golden Gun is for {hero}"
        )
    except IndexError:
        return await ctx.message.channel.send(
            "{} is a liar!, They don't have every golden gun!".format(
                ctx.message.author.mention
            )
        )


@command(pass_context=True)
async def quote(ctx):
    quotes_channel = discord.utils.get(ctx.guild.channels, name="quotes")
    quotes = []
    async for q in discord.iterators.HistoryIterator(quotes_channel, 100):
        quotes.append(q)
    return await ctx.message.channel.send(random.choice(quotes).content)


@command(pass_context=True)
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


@command(pass_context=True)
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


@command(pass_context=True)
async def toggle_role(ctx):
    """
    Toggles given role on or off
    for example:
            "toggle_role overwatch"
            will add or remove the overwatch role
    Try "roles" for Currently Toggleable Roles
    """
    # gets toggleable Roles
    """
    toggleable_roles = []
    for role in ctx.message.channel.guild.roles:
        if str(role.color) == "#206694":
            toggleable_roles += [
                role.name,
            ]
    """

    toggleable_roles = {
        role.name.lower(): role
        for role in ctx.message.channel.guild.roles
        if str(role.color) == "#206694"
    }

    try:
        parsed_roles = [r.lower() for r in ctx.message.content.split()][1:]
        print(f"{parsed_roles=}")
        role_to_toggle = toggleable_roles[parsed_roles[0]]
        print(f"{toggleable_roles=}")

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

    except IndexError:
        await ctx.message.channel.send("Could not parse roles")
    except KeyError:
        await ctx.message.channel.send(
            f'Role Not Found, try "{ctx.bot.command_prefix}roles" for '
            "a list of toggleable roles, be sure to check your spelling too."
        )


@command(pass_context=True)
async def hello(ctx):
    """
    Says Hello to whomever called it
    """
    msg = "Hi {0.author.mention}".format(ctx.message)
    await ctx.message.channel.send(msg)


@command(pass_context=True)
async def heros(ctx):
    msg = ""
    for k in OW_HEROS:
        msg += "{}: {}\n".format(k, OW_HEROS[k])
    await ctx.message.channel.send(msg)


@command(pass_context=True)
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


@command(pass_context=True)
async def thanks(ctx):
    await ctx.message.channel.send(
        "You're Welcome {}!".format(ctx.message.author.mention)
    )


@command()
async def echo(ctx):
    return await ctx.message.channel.send(
        ctx.message.content.removeprefix(f"{ctx.bot.command_prefix}echo")
    )


@command()
async def cs(ctx):
    imgs = [
        "bella_cs_chart.png",
        "magnizar_cs_chart.png",
    ]
    dir_ = BASE_DIR / "static" / random.choice(imgs)
    return await ctx.message.channel.send(file=discord.File(dir_))
