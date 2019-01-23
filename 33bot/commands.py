from constants import TOGGLEABLE_ROLES, PREFIX, OVERWATCH_HEROS
import discord
import random


# define commands
async def golden_gun(message):
    """
    Choose the next Overwatch Golden Gun for you to get.
    For Example:
            "golden_gun 1 8 15 24 28"
            Where the numbers are the heros who you already have golden guns for
            Try "heros" for hero-number pairs
    """
    try:
        owned = [int(x) for x in message.content.split()[1:]]
    except ValueError:
        return await message.channel.send("{}, arguments must be numeric, try 'heros' for a list of hero-number pairs"
                                          .format(message.author.mention))
    try:
        return await message.channel.send("{}, Your next Golden Gun is for {}!".format(
                                          message.author.mention,
                                          OVERWATCH_HEROS[random.choice(list((OVERWATCH_HEROS.keys() ^ owned)))]))
    except IndexError:
        return await message.channel.send("{} is a liar!, They dont have every golden gun!"
                                          .format(message.author.mention))


async def random_num(message):
    """
    Gets a Random integer between 0 and given max
    For example:
            "random_number 3"
            will return a 0, 1, 2, or 3
    """
    max_num = int(message.content.split()[1])
    return await message.channel.send('{},\tYour random number (between 0 and {}) is: {}'
                                      .format(message.author.mention, max_num, random.randint(0, max_num)))


async def roles(message):
    """
    Displays Your current roles as well as the currently toggleable roles
    """
    current_roles = [r.name for r in reversed(message.author.roles)][:-1]
    your_toggleable_roles = []
    for r in TOGGLEABLE_ROLES:
        if r in current_roles:
            your_toggleable_roles += ['**' + r + '**', ]
        else:
            your_toggleable_roles += [r, ]

    msg = "Your Current Roles: {}\nToggleable Roles: {}".format(current_roles, your_toggleable_roles)
    return await message.channel.send("{}:\n{}".format(message.author.mention, msg))


async def toggle_role(message):
    """
    Toggles given role on or off
    for example:
            "toggle_role overwatch"
            will add or remove the overwatch role
    Try "roles" for Currently Toggleable Roles
    """
    try:
        role_to_toggle = message.content.split()[1]

        if role_to_toggle in TOGGLEABLE_ROLES:  # Checks to See if given role is toggleable
            role_to_toggle = discord.utils.get(message.channel.guild.roles, name=role_to_toggle)

            # Toggle role
            if role_to_toggle in message.author.roles:  # Removes Role
                await message.author.remove_roles(role_to_toggle)
                await message.channel.send("{}: Role removed".format(message.author.mention))
            else:  # Gives Role
                await message.author.add_roles(role_to_toggle)
                await message.channel.send("{}: Role Added".format(message.author.mention))

        # Role is not toggleable
        else:
            await message.channel.send('Role Not Found, try "{}roles" for a list of toggleable roles'.format(PREFIX))

    # Checks to see if a role was given
    except IndexError:
        await message.channel.send('You must add a valid role, try "{}help" for help'.format(PREFIX))


# Hidden Commands ---------------------------
async def hello(message):
    """
    Says Hello to whomever called it
    """
    msg = 'Hi {0.author.mention}'.format(message)
    await message.channel.send(msg)


async def heros(message):
    msg = ''
    for k in OVERWATCH_HEROS:
        msg += '{}: {}\n'.format(k, OVERWATCH_HEROS[k])
    await message.channel.send(msg)


async def roll_the_dice(message):
    await message.channel.send("Nothing's Here. Any Suggestions?")


async def thanks(message):
    await message.channel.send("You're Welcome {}!".format(message.author.mention))


# Help Command --------------------------------------
async def command_help(message):
    """
    Displays Available Commands
    """
    msg = "Available Commands:\n\tPrefix: '{}'\n".format(PREFIX)
    for c in commands:
        msg += '\n"{}": \n {} {}'.format(c, '-'*(len(c) + 3), commands[c].__doc__)
    await message.channel.send(msg)


async def command_not_recognised(message):
    msg = 'Command:   "{}"   Not Recognised,\n\tTry "{}help" for a list of commands' \
        .format(message.content, PREFIX)
    await message.channel.send(msg)


# Dict containing all possible commands
commands = {
            'golden_gun': golden_gun,
            'random_number': random_num,
            'roles': roles,
            'toggle_role': toggle_role,
            }
hidden_commands = {'hello': hello,
                   'heros': heros,
                   'rtd': roll_the_dice,
                   'thankyou': thanks,
                   'thanks': thanks,
                   'help': command_help,
                   }
