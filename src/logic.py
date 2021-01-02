"""
This file contains the logic behind each
command defined in `commands.py
"""
from prettytable import PrettyTable

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


def roles(message):
    """
    Displays Your current roles as well as the currently toggleable roles
    """
    # Generate Data
    toggleable_roles = {
        # reversed puts the roles in alphabetical order for some reason
        r: False for r in reversed(message.channel.guild.roles) if str(r.color) == "#206694"
    }
    for k in toggleable_roles.keys():
        if k in message.author.roles:
            toggleable_roles[k] = True

    # Format Roles to table
    table = PrettyTable()
    table.align = "c"
    table.field_names = ["Toggleable Roles", "Status"]

    for k, v in toggleable_roles.items():
        table.add_row([k.name, '✅' if v else ''])

    return "```\n" + table.get_string() + "\n```"


async def toggle_role(author, roles: list):
    out = f"{author.mention}:\n"
    for r in roles:
        if r in author.roles:  # Removes Role
            out += f"\t{r.name} removed\n"
            await author.remove_roles(r)
        else:  # Gives Role
            out += f"\t{r.name} added\n"
            await author.add_roles(r)
    return out

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


def cs() -> os.Pathlib:
    imgs = [
        "bella_cs_chart.png",
        "magnizar_cs_chart.png",
    ]
    dir_ = BASE_DIR / "static" / random.choice(imgs)
    return dir_
