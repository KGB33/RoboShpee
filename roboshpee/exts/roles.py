import asyncio
from typing import Final, Iterable, Optional

import discord
from discord.ext import commands
from fuzzywuzzy import process
from prettytable import PrettyTable

from roboshpee.bot import Bot
from roboshpee.constants import (
    ELDER_SHPEE,
    MASTER_SHPEE,
    SENOR_SHPEE,
    TOGGLEABLE_GAME_ROLE_COLOR,
)
from roboshpee.security import minimum_role_permission
from roboshpee.utils import msg_owner, ttl_cache


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
@minimum_role_permission(ELDER_SHPEE)
async def create(ctx, name):
    """
    Creates a new @Game role.

    Requires Elder Shpee role or greater to start a vote.
    """
    REQUIRED_VOTES: Final = 12
    SENTINAL_VOTES: Final = 333
    vote_state = {"yes": 0, "no": 0}
    vote_values = {MASTER_SHPEE: 4, ELDER_SHPEE: 3, SENOR_SHPEE: 2}
    msg_template = (
        "Vote to ✅-Yes or ❌-No to create _{name}_."
        "\n\nCurrent Votes:"
        "\n\tYes: {yes_votes}/{REQUIRED_VOTES}"
        "\n\tNo: {no_votes}/{REQUIRED_VOTES}"
    )
    msg = await ctx.send(
        msg_template.format(
            name=name,
            REQUIRED_VOTES=REQUIRED_VOTES,
            yes_votes=vote_state["yes"],
            no_votes=vote_state["no"],
        )
    )
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(r):
        return (
            (str(r.emoji) in ("❌", "✅"))
            and (r.message_id == msg.id)
            and (r.user_id != ctx.bot.user.id)
        )

    # Wait for reactions until the required number of votes has been reached.
    while (vote_state["yes"] < REQUIRED_VOTES) and (vote_state["no"] < REQUIRED_VOTES):
        # TODO: Fix race conditions when multiple people react at almost the same time
        reaction_group = {
            asyncio.create_task(ctx.bot.wait_for("raw_reaction_add", check=check)),
            asyncio.create_task(ctx.bot.wait_for("raw_reaction_remove", check=check)),
        }
        finished, _ = await asyncio.wait(
            reaction_group, return_when=asyncio.FIRST_COMPLETED
        )
        assert len(finished) == 1
        reaction = list(finished)[0].result()

        yei_or_nei = "yes" if str(reaction.emoji) == "✅" else "no"
        if ctx.guild.owner_id == reaction.user_id:
            vote_state[yei_or_nei] = SENTINAL_VOTES
            msg_template += (
                f"\n**{'Approved' if yei_or_nei == 'yes' else 'Rejected'}** by KGB.33"
            )
        elif (ctx.author.id == reaction.user_id) and (yei_or_nei == "no"):
            vote_state["no"] = SENTINAL_VOTES
            msg_template += f"\n**Withdrawn** by {ctx.author}"
        else:
            voting_user = await ctx.guild.fetch_member(reaction.user_id)
            if reaction.event_type == "REACTION_ADD":
                vote_state[yei_or_nei] += vote_values.get(voting_user.roles[-1].id, 1)
            elif reaction.event_type == "REACTION_REMOVE":
                vote_state[yei_or_nei] -= vote_values.get(voting_user.roles[-1].id, 1)

        await msg.edit(
            content=msg_template.format(
                name=name,
                REQUIRED_VOTES=REQUIRED_VOTES,
                yes_votes=vote_state["yes"],
                no_votes=vote_state["no"],
            )
        )
    result = vote_state["yes"] > vote_state["no"]
    if SENTINAL_VOTES not in vote_state.values():
        await msg.edit(
            content=(
                msg.content + f"\n**{'Approved' if result else 'Rejected'}** by Vote"
            )
        )
    if result:
        # Create the Role
        await _create_role(ctx, name)


async def _create_role(ctx, name: str):
    """
    Handles the creation and permissions of
    new roles created for @game mentions.
    """
    await ctx.guild.create_role(
        reason="Created by vote.",
        name=name,
        mentionable=True,
        color=TOGGLEABLE_GAME_ROLE_COLOR,
    )
    await msg_owner(ctx, f"A new role was created `{name}`")


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
        role.name.lower(): role
        for role in guild.roles
        if role.color == TOGGLEABLE_GAME_ROLE_COLOR
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
