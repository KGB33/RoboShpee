import logging
from typing import Final, Iterable, Literal

import discord
from discord.ext import commands
from fuzzywuzzy import process
from prettytable import PrettyTable

from roboshpee.bot import Bot
from roboshpee.constants import (
    ELDER_SHPEE,
    MASTER_SHPEE,
    OWNER,
    PREFIX,
    SENOR_SHPEE,
    TOGGLEABLE_GAME_ROLE_COLOR,
)
from roboshpee.menu import ReactionMenu, ReactionMenuOption
from roboshpee.security import minimum_role_permission, requires_exact_role
from roboshpee.utils import msg_owner, ttl_cache

log = logging.getLogger(name="bot")


@commands.hybrid_group()
async def role(ctx):
    if ctx.invoked_subcommand is not None:
        return
    await list_(ctx)


@role.command(name="list")
async def list_(ctx, orderby: Literal["count", "name", "member"] = "name"):
    """
    Displays all toggleable roles.
    """
    await ctx.defer()
    toggleable_roles = [
        {"count": len(r.members), "name": r.name, "member": (r in ctx.author.roles)}
        for r in _fetch_toggleable_roles(ctx.guild).values()
    ]

    # Format Roles to table
    table = PrettyTable()
    # table.align = "c"
    table.field_names = ["Members", "Role", "Status"]

    for role in sorted(
        toggleable_roles, key=lambda r: r[orderby], reverse=(orderby != "name")
    ):
        table.add_row([role["count"], role["name"], "✅" if role["member"] else "  "])

    output = table.get_string()
    if len(output) > 1992:
        output = output[:1992]
    return await ctx.send(f"```\n{output}\n```")


@role.command()
@minimum_role_permission(ELDER_SHPEE)
async def create(ctx, name):
    """
    Creates a new @Game role.

    Requires Elder Shpee role or greater to start a vote.
    """
    log.info(f"Recived request to create role: '{name}'")
    REQUIRED_VOTES: Final = 12
    YES_IDX, NO_IDX = 0, 1
    YES_NAME, NO_NAME = "✅-Yes", "❌-No"

    embed = discord.Embed(
        title=f"Create new role `@{name}`?",
        description="Vote ✅-Yes or ❌-No to create the new role",
        color=TOGGLEABLE_GAME_ROLE_COLOR,
    )
    embed.insert_field_at(YES_IDX, name=YES_NAME, value="No Votes Yet.")
    embed.insert_field_at(NO_IDX, name=NO_NAME, value="No Votes Yet.")
    msg = await ctx.send(embed=embed)

    def on_reaction_event_factory(embed, embed_idx, msg, name: str, value: str):
        async def wrapped(self: ReactionMenuOption):
            embed.set_field_at(
                index=embed_idx, name=name, value=value.format(self.state)
            )
            await msg.edit(embed=embed)

        return wrapped

    def generate_reation_value(ctx):
        async def calculate_reaction_value(r: discord.RawReactionActionEvent) -> int:
            voting_user = await ctx.guild.fetch_member(r.user_id)
            vote_values = {
                OWNER: REQUIRED_VOTES,
                MASTER_SHPEE: 4,
                ELDER_SHPEE: 3,
                SENOR_SHPEE: 2,
            }
            return vote_values.get(voting_user.roles[-1].id, 1)

        return calculate_reaction_value

    YES_reaction_event = on_reaction_event_factory(
        embed, YES_IDX, msg, YES_NAME, value="{}/" + str(REQUIRED_VOTES)
    )
    NO_reaction_event = on_reaction_event_factory(
        embed, NO_IDX, msg, NO_NAME, value="{}/" + str(REQUIRED_VOTES)
    )

    calc_value_func = generate_reation_value(ctx)

    def generate_yes_callback(ctx, r_name):
        async def wrapped():
            await _create_role(ctx, r_name)

        return wrapped

    options = {
        "✅": ReactionMenuOption(
            callback_func=generate_yes_callback(ctx, name),
            on_reaction_add=YES_reaction_event,
            on_reaction_remove=YES_reaction_event,
            calculate_reaction_value=calc_value_func,
            callback_trigger=REQUIRED_VOTES,
        ),
        "❌": ReactionMenuOption(
            callback_func=lambda: print("No Won"),
            on_reaction_add=NO_reaction_event,
            on_reaction_remove=NO_reaction_event,
            calculate_reaction_value=calc_value_func,
            callback_trigger=REQUIRED_VOTES,
        ),
    }
    menu = await ReactionMenu.create(ctx, msg, "", options)
    await menu.wait_for_results()


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
@requires_exact_role(OWNER)
async def delete(ctx, role_name: str):
    """
    Deletes a role, can only be preformed by the owner.
    """
    await ctx.defer()
    toggleable_roles = _fetch_toggleable_roles(ctx.guild)
    role = toggleable_roles.get(role_name.lower(), None)
    if role is None:
        return await _handle_invalid_roles(
            ctx,
            {
                role_name,
            },
        )
    await role.delete(
        reason=f"Removed by {ctx.author.name} via `{PREFIX}role delete {role_name}`"
    )
    return await ctx.send(f"Deleted {role_name}.")


@role.command()
async def toggle(ctx, role: str):
    await toggle_multiple(ctx, role)


@role.command(with_app_command=False)
async def toggle_multiple(ctx, *roles):
    """
    Toggle the provided roles on or off.

    Examples:
        >>> role toggle Overwatch TeamFortressTwo
        Added Overwatch
        Removed TeamFortressTwo
    """
    await ctx.defer()
    # Parse input data
    validated_roles, invalid_roles = _validate_role_input(roles, ctx.guild)

    # Handle invalid data
    await _handle_invalid_roles(ctx, invalid_roles)

    # Process valid data
    author = ctx.message.author
    msg = ""
    for r in validated_roles:
        if r in author.roles:
            msg += f"\tRemoved: `{r.name}`\n"
            await author.remove_roles(r)
        else:
            msg += f"\tAdded:   `{r.name}`\n"
            await author.add_roles(r)
    if msg:
        return await ctx.send(msg)


@role.command()
async def add(ctx, role: str):
    return await add_multiple(ctx, role)


@role.command(with_app_command=False)
async def add_multiple(ctx, *roles):
    """
    Add yourself to the supplied roles.

    Examples:
        >>> role toggle Overwatch TeamFortressTwo
        Added Overwatch
        Added TeamFortressTwo
    """
    await ctx.defer()
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
    if msg:
        return await ctx.send(msg)


@role.command()
async def remove(ctx, role: str):
    """
    Remove yourself from a given role.
    """
    await remove_multiple(ctx, role)


@role.command(with_app_command=False)
async def remove_multiple(ctx, *roles):
    """
    Remove yourself from the supplied roles.

    Examples:
        >>> role toggle Overwatch TeamFortressTwo
        Removed: Overwatch
        Removed: TeamFortressTwo
    """
    await ctx.defer()
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
    if msg:
        return await ctx.send(msg)


async def _handle_invalid_roles(ctx, roles: Iterable[str]):
    for role in roles:
        suggested = _suggest_corrections(
            role, (_fetch_toggleable_roles(ctx.guild).keys()), limit=3
        )
        if suggested:
            await ctx.send(
                f"`{role}` isn't a valid role, perhaps you meant one of `{suggested}`"
            )
        else:
            await ctx.send(
                f"`{role}` isn't a valid role, no close matches could be found."
            )
        await ctx.send("The `slash` commands also provide autocomplete!")


@add.autocomplete("role")
@toggle.autocomplete("role")
@remove.autocomplete("role")
@delete.autocomplete("role_name")
async def role_autocompleation(
    interaction: discord.Interaction, current: str
) -> list[discord.app_commands.Choice[str]]:
    roles = _fetch_toggleable_roles(interaction.guild).keys()
    if current == "":
        return [discord.app_commands.Choice(name=r, value=r) for r in roles][:25]
    corrections = _suggest_corrections(current, roles, limit=20)
    return [discord.app_commands.Choice(name=r, value=r) for r in corrections]


@ttl_cache()
def _fetch_toggleable_roles(guild: discord.Guild) -> dict[str, discord.Role]:
    return {
        role.name.lower(): role
        for role in guild.roles
        if role.color == TOGGLEABLE_GAME_ROLE_COLOR
    }


def _suggest_corrections(word: str, roles: Iterable[str], limit=1) -> list[str]:
    """
    For each incorrect spelling,
        fuzzy find the closest match (above the cut-off)
    Then, return the {incorrect: suggested} pairs
    """
    if results := process.extract(word, roles, limit=limit):
        return [r[0] for r in results if r[1] > 66]
    return []


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


async def setup(bot: Bot) -> None:
    bot.add_command(role)
