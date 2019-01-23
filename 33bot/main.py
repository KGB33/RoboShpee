import discord
import logging
import asyncio
from not_so_secret import TOKEN  # TODO: Figure out how venv variables work
from constants import PREFIX
from commands import commands, hidden_commands, command_not_recognised

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


@client.event
async def on_message(message):
    # Prevent bot from replying to itself
    if message.author == client.user:
        return

    # Check PREFIX
    if message.content[:3] == PREFIX:
        # Log message and message info
        logger.info("\tMessage: \n\t\t{}\n\n\tWas sent by {}\n\tIn {} Channel\n\n\n"
                    .format(message.content, message.author, message.channel))

        # trim PREFIX from message
        message.content = message.content[3:].lower().strip()

        try:
            task = asyncio.create_task(commands[message.content.split()[0]](message))
        except KeyError:
            try:
                task = asyncio.create_task(hidden_commands[message.content.split()[0]](message))
            except KeyError:
                task = asyncio.create_task(command_not_recognised(message))

        await task


@client.event
async def on_ready():
    print("Logged in as:")
    print(client.user.name)
    print(client.user.id)
    print('--------------\n\n')

client.run(TOKEN)
