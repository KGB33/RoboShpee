"""
This file contains input validation for
each command.
"""
import random

from src.constants import OW_HEROS, SHAXX_QUOTES
from src import BASE_DIR, log, PREFIX


def golden_gun(content, author) -> (set, str):
    """
    Choose the next Overwatch Golden Gun for you to get.
    For Example:
            "golden_gun 1 8 15 24 28"
            Where the numbers are the heros who you already have golden guns
            for. Try "heros" for hero-number pairs
    """
    owned = content.removeprefix(f"{PREFIX}golden_gun").split()
    if invalid_digits := [x for x in owned if not x.isdigit()]:
        return (
            None,
            f"{author.mention}, the following could not be parsed to an integer.\n"
            f"Try the `heros` command for a list of valid inputs\n\t{invalid_digits}",
        )

    if invalid_heros := [x for x in owned if int(x) not in OW_HEROS.keys()]:
        return (
            None,
            f"{author.mention}, the following digits do not correspond to a valid hero.\n"
            f"Try the `heros` command for a list of valid inputs\n\t{invalid_heros}",
        )
    return {int(x) for x in owned}, None


def random_num(content: str) -> ((int, int), str):
    """
    Gets a Random integer between an optional min (default zero)
    and the given max.
    For example:
            "random_number 3"
            will return a 0, 1, 2, or 3
    """
    content = content.removeprefix(f"{PREFIX}random_num").strip()
    try:
        nums = [int(x) for x in content.split()]
    except ValueError:
        return None, f"Could not parse `{content.split()}` to integers"

    l = len(nums)
    if l not in (1, 2):
        return (
            None,
            f"Parsed an incorrect number of digits, expected one or two, got {l}.",
        )
    if len(nums) == 1:
        nums.append(0)
    return tuple(sorted(nums)), None


def toggle_role(content, channel) -> (list, str):
    """
    First it parses the input into a list of roles.
    Then it ensures that each role is valid.

    If all roles are valid:
        the first return value is a list of roles
        and the second is None
    else:
        the first return value is None,
        and the second is a error message.
    """
    content = content.removeprefix(f"{PREFIX}toggle_role")
    # gets toggleable Roles
    toggleable_roles = {
        role.name.lower(): role
        for role in channel.guild.roles
        if str(role.color) == "#206694"
    }

    # parse input
    parsed_roles = {r.lower() for r in content.split()}
    if invalid_roles := parsed_roles - toggleable_roles.keys():
        return (
            None,
            f"The following roles are invalid, please check your spelling and try again\n{invalid_roles}",
        )
    return [
        r for r in toggleable_roles.values() if r.name.lower() in parsed_roles
    ], None
