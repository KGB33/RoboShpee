import discord
from discord.ext import commands
from prettytable import PrettyTable

from roboshpee.bot import Bot


@commands.group()
async def role(ctx):
    """
    Displays all toggleable roles.
    """
    if ctx.invoked_subcommand is not None:
        return
    # Generate Data
    toggleable_roles = {
        # reversed puts the roles in alphabetical order for some reason
        r: False
        for r in reversed(ctx.message.channel.guild.roles)
        if str(r.color) == "#206694"
    }
    for k in toggleable_roles.keys():
        if k in ctx.message.author.roles:
            toggleable_roles[k] = True

    # Format Roles to table
    table = PrettyTable()
    table.align = "c"
    table.field_names = ["Toggleable Roles", "Status"]

    for k, v in toggleable_roles.items():
        table.add_row([k.name, "✅" if v else ""])

    return await ctx.send(f"{ctx.author.mention}\n```\n" + table.get_string() + "\n```")


@role.command()
async def toggle(ctx, *roles):
    """
    Toggle the provided roles on or off.

    Examples:
        >>> role toggle Overwatch TeamFortressTwo
        Added Overwatch
        Removed TeamFortressTwo
    """
    # gets toggleable Roles
    roles, inval_roles = validate_role_input(roles, ctx.guild)
    if inval_roles:
        inval_roles_formatted = " ".join(f"`{r}`" for r in reversed(inval_roles))
        await ctx.send(
            "The following roles are invalid, please check your spelling"
            f" and try again\n\t {inval_roles_formatted}"
        )
    author = ctx.message.author
    msg = f"{author.mention}:\n"
    for r in roles:
        if r in author.roles:  # Removes Role
            msg += f"\tRemoved: {r.name}\n"
            await author.remove_roles(r)
        else:  # Gives Role
            msg += f"\tAdded:   {r.name}\n"
            await author.add_roles(r)
    return await ctx.message.channel.send(msg)


@role.command()
async def add(ctx, *roles):
    """
    Add yourself to the supplied roles.
    """
    roles
    print(f"Added: {roles}")


@role.command
async def remove(ctx, *roles):
    """
    Remove yourself from the supplied roles.
    """
    print(f"removed: {roles}")


def validate_role_input(
    roles: list[str], guild: discord.guild
) -> (list[str], list[str]):
    """
    First it parses the input into a list of roles.
    Then it ensures that each role is valid.

    The First return value is the valid roles
    The Second return value is the invalid roles
    """
    # gets toggleable Roles
    toggleable_roles = {
        role.name.lower(): role for role in guild.roles if str(role.color) == "#206694"
    }
    # parse input
    parsed_roles = {r.lower() for r in roles}
    invalid_roles = parsed_roles - toggleable_roles.keys()
    valid_roles = [
        r for r in toggleable_roles.values() if r.name.lower() in parsed_roles
    ]
    return valid_roles, invalid_roles


def setup(bot: Bot) -> None:
    bot.add_command(role)
