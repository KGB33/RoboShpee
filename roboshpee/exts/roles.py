from typing import Optional, Iterable

import discord
from discord.ext import commands
from prettytable import PrettyTable
from fuzzywuzzy import process

from roboshpee.bot import Bot
from roboshpee.utils import ttl_cache


@commands.group()
async def role(ctx):
    """
    Displays all toggleable roles.
    """
    if ctx.invoked_subcommand is not None:
        return

    toggleable_roles = {
        r: (r in ctx.author.roles) for r in _fetch_toggleable_roles(ctx.guild).values()
    }

    # Format Roles to table
    table = PrettyTable()
    table.align = "c"
    table.field_names = ["Toggleable Roles", "Status"]

    for role in sorted(toggleable_roles.keys(), key=lambda r: r.name):
        # This uses a white_check_mark to denote if the user has the role
        # It might look weird on devices without that codepoint
        # If you're unsure if its working check the bot's response on
        # your phone
        table.add_row([role.name, "✅" if toggleable_roles[role] else "  "])

    return await ctx.send(f"```\n{ctx.author.name}\n" + table.get_string() + "\n```")


@role.command()
async def toggle(ctx, *roles):
    """
    Toggle the provided roles on or off.

    Examples:
        >>> role toggle Overwatch TeamFortressTwo
        Added Overwatch
        Removed TeamFortressTwo
    """
    # Parse input data
    validated_roles, invalid_roles = _validate_role_input(roles, ctx.guild)

    # Handle invalid data
    await _handle_invalid_roles(ctx, invalid_roles)

    # Process valid data
    author = ctx.message.author
    msg = ""
    for r in validated_roles:
        if r in author.roles:  # Removes Role
            msg += f"\tRemoved: `{r.name}`\n"
            await author.remove_roles(r)
        else:  # Gives Role
            msg += f"\tAdded:   `{r.name}`\n"
            await author.add_roles(r)
    return await ctx.message.channel.send(msg)


@role.command()
async def add(ctx, *roles):
    """
    Add yourself to the supplied roles.

    Examples:
        >>> role toggle Overwatch TeamFortressTwo
        Added Overwatch
        Added TeamFortressTwo
    """
    roles, inval_roles = _validate_role_input(roles, ctx.guild)
    if inval_roles:
        await _handle_invalid_roles(ctx, inval_roles)
    author = ctx.message.author
    msg = ""
    for r in roles:
        if r in author.roles:  # Removes Role
            msg += f"\tYou already have this role: `{r.name}`\n"
        else:  # Gives Role
            msg += f"\tAdded:   `{r.name}`\n"
            await author.add_roles(r)
    return await ctx.message.channel.send(msg)


@role.command()
async def remove(ctx, *roles):
    """
    Remove yourself from the supplied roles.

    Examples:
        >>> role toggle Overwatch TeamFortressTwo
        Removed: Overwatch
        Removed: TeamFortressTwo
    """
    roles, inval_roles = _validate_role_input(roles, ctx.guild)
    if inval_roles:
        await _handle_invalid_roles(ctx, inval_roles)
    author = ctx.message.author
    msg = ""
    for r in roles:
        if r in author.roles:  # Removes Role
            msg += f"\tRemoved: `{r.name}`\n"
            await author.remove_roles(r)
        else:
            msg += f"\tYou don't have the following role:  `{r.name}`\n"
    return await ctx.message.channel.send(msg)


async def _handle_invalid_roles(ctx, roles: Iterable[str]):
    for incorrect, suggested in _suggest_corrections(
        roles, (_fetch_toggleable_roles(ctx.guild).keys())
    ).items():
        if suggested is not None:
            await ctx.send(
                f"`{incorrect}` isn't a valid role, perhaps you meant `{suggested}`"
            )
        else:
            await ctx.send(
                f"`{incorrect}` isn't a valid role, and no close matches could be found."
            )


@ttl_cache()
def _fetch_toggleable_roles(guild: discord.Guild) -> dict[str, discord.Role]:
    return {
        role.name.lower(): role for role in guild.roles if str(role.color) == "#206694"
    }


def _suggest_corrections(
    incorrect_spellings: Iterable[str], roles: Iterable[str]
) -> dict[str, Optional[str]]:
    """
    For each incorrect spelling,
        fuzzy find the closest match (above the cut-off)
    Then, return the {incorrect: suggested} pairs
    """
    output = dict()
    for word in incorrect_spellings:
        if (
            fuzzy_match := process.extractOne(word, roles, score_cutoff=50)
        ) is not None:
            output[word] = fuzzy_match[0]
        else:
            output[word] = None
    return output


def _validate_role_input(
    roles: Iterable[str], guild: discord.Guild
) -> tuple[set[discord.Role], set[str]]:
    """
    Splits the input data into valid and invalid
    """
    toggleable_roles = _fetch_toggleable_roles(guild)
    normalized_input = {r.lower() for r in roles}
    valid_roles = {
        r for r in toggleable_roles.values() if r.name.lower() in normalized_input
    }
    invalid_roles = {
        word for word in normalized_input if word.lower() not in toggleable_roles.keys()
    }
    return valid_roles, invalid_roles


def setup(bot: Bot) -> None:
    bot.add_command(role)
