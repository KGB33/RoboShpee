"""
This file contains the logic behind each
command defined in `commands.py
"""
import random

from src.constants import OW_HEROS, SHAXX_QUOTES
from src import BASE_DIR, log


def golden_gun(owned: set):
    return OW_HEROS[random.choice(list((OW_HEROS.keys() ^ owned)))]


def quote(quotes: list):
    return random.choice(quotes).content


def random_num(lower: int, upper: int) -> str:
    """
    Gets a Random integer between 0 and given max
    For example:
            "random_number 3"
            will return a 0, 1, 2, or 3
    """
    return f"Your random number (between {lower} and {upper}) is: {random.randint(lower, upper)}"


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


async def toggle_role(ctx):
    """
    Toggles given role on or off
    for example:
            "toggle_role overwatch"
            will add or remove the overwatch role
    Try "roles" for Currently Toggleable Roles
    """
    # gets toggleable Roles
    toggleable_roles = {
        role.name.lower(): role
        for role in ctx.message.channel.guild.roles
        if str(role.color) == "#206694"
    }

    try:
        parsed_roles = [r.lower() for r in ctx.message.content.split()][1:]
        log.info(f"{parsed_roles=}")
        role_to_toggle = toggleable_roles[parsed_roles[0]]
        log.info(f"{toggleable_roles=}")

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
        keyErrMsg = f'Role Not Found, try "{ctx.bot.command_prefix}roles" for '
        +"a list of toggleable roles, be sure to check your spelling too."
        log.warn(keyErrMsg)
        await ctx.message.channel.send(keyErrMsg)


async def hello(ctx):
    """
    Says Hello to whomever called it
    """
    msg = "Hi {0.author.mention}".format(ctx.message)
    await ctx.message.channel.send(msg)


async def heros(ctx):
    msg = ""
    for k in OW_HEROS:
        msg += "{}: {}\n".format(k, OW_HEROS[k])
    await ctx.message.channel.send(msg)


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


async def thanks(ctx):
    await ctx.message.channel.send(
        "You're Welcome {}!".format(ctx.message.author.mention)
    )


async def echo(ctx):
    return await ctx.message.channel.send(
        ctx.message.content.removeprefix(f"{ctx.bot.command_prefix}echo")
    )


async def cs(ctx):
    imgs = [
        "bella_cs_chart.png",
        "magnizar_cs_chart.png",
    ]
    dir_ = BASE_DIR / "static" / random.choice(imgs)
    log.info(f"`cs` was called, {dir_} returned")
    return await ctx.message.channel.send(file=discord.File(dir_))
