import discord
import logging
import asyncio
from not_so_secret import TOKEN  # TODO: Figure out how venv variables work

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('33bot.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Set up discord client
client = discord.Client()

# message prefix that the bot will respond to
PREFIX = '!3.'
# Toggleable roles on the server
TOGGLEABLE_ROLES = ['Brawlhalla', 'Civilization', 'Dauntless', 'Destiny2', 'DJ', 'Overwatch', 'SmashBros', ]


@client.event
async def on_message(message):
    # Prevent bot from replying to itself
    if message.author == client.user:
        return

    # Check PREFIX
    if message.content[:3] == PREFIX:
        # Log message and message info
        logger.info("\n\n\n\tMessage: \n\t\t{}\n\n\tWas sent by {}\n\tIn {} Channel"
                    .format(message.content, message.author, message.channel))

        # trim PREFIX from message
        message.content = message.content[3:]

        # define commands
        async def hello():
            """
            Says Hello to whomever called it
            """
            msg = 'Hi {0.author.mention}'.format(message)
            await message.channel.send(msg)

        async def roles():
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
            await message.channel.send("{}:\n{}".format(message.author.mention, msg))

        async def toggle_role():
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
                    await message.channel.send('Role Not Found, try "{}help" for help'.format(PREFIX))

            # Checks to see if a role was given
            except IndexError:
                await message.channel.send('You must add a valid role, try "{}help" for help'.format(PREFIX))

        async def command_help():
            """
            Displays Available Commands
            """
            msg = "Available Commands:\n\tPrefix: '{}'\n".format(PREFIX)
            for c in commands:
                msg += '\n"{}": \n {} {}'.format(c, '-'*(len(c) + 3), commands[c].__doc__)
            await message.channel.send(msg)

        async def command_not_recognised():
            msg = 'Command:   "{}"   Not Recognised,\n\tTry "{}help" for a list of commands' \
                .format(message.content, PREFIX)
            logger.info('\n Command not recognised: {}'.format(message.content))
            return await message.channel.send(msg)

        # Dict containing all possible commands
        commands = {'hello': hello,
                    'roles': roles,
                    'toggle_role': toggle_role,
                    'help': command_help,
                    }
        try:
            task = asyncio.create_task(commands[message.content.split()[0]]())
        except KeyError:
            task = asyncio.create_task(command_not_recognised())

        await task


@client.event
async def on_ready():
    print("Logged in as:")
    print(client.user.name)
    print(client.user.id)
    print('--------------\n\n')

client.run(TOKEN)
