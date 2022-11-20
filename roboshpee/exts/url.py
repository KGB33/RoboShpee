import requests
from discord.ext import commands
from prettytable import PrettyTable

from roboshpee.bot import Bot

"""
Note: this requires that another one of my projects
is running on the same device (and at port 8080)
See https://github.com/KGB33/url-shortener for more info.
"""
API_URL = "http://0.0.0.0:8080/api/v1"


@commands.group()
async def url(ctx):
    # Check to see if the url server is up before running any commands
    try:
        requests.get(API_URL)
    except requests.exceptions.ConnectionError:
        ctx.invoked_subcommand = None
        return await ctx.send(
            "The URL service is not running. No `url` commands will work."
        )

    if ctx.invoked_subcommand is not None:
        return

    r = requests.get(API_URL + "/r")
    data = r.json()
    if isinstance(data, dict):
        return await ctx.send(f"Server returned an error: {data['message']}")

    table = PrettyTable()
    table.align = "c"
    table.field_names = ["Key", "Destination Url"]

    for u in data:
        table.add_row([u["ShortUrl"], u["DestUrl"]])
    return await ctx.send(f"```\n{table.get_string()}\n```")


@url.command()
async def redirect(ctx, key: str):
    """
    Retrieves the destination URL matching
    the key/shortened URL provided

    Examples:
        >>> url redirect FizzBuzz
        https://www.youtube.com/watch?v=QPZ0pIK_wsc
    """


@url.command()
async def create(ctx, *args):
    """
    Creates a shortened URL based off the information provided.
    Format:
        url create [key] destination_url

    Examples:
        >>> url create FizzBuzz https://www.youtube.com/watch?v=QPZ0pIK_wsc
        Created key `FizzBuzz` that redirects to `https://www.youtube.com/watch?v=QPZ0pIK_wsc`

        >>> url create https://github.com/KGB33/url-shortener
        Created key `FU4yMyyYZnF` that redirects to `https://github.com/KGB33/url-shortener`
    """  # noqa: E501 (Line too long)
    if len(args) == 1:
        shortUrl = ""
        destUrl = args[0]
    elif len(args) == 2:
        shortUrl = args[0]
        destUrl = args[1]
    else:
        return await ctx.send("Could not parse args...")

    r = requests.post(API_URL + "/c", json={"ShortUrl": shortUrl, "DestUrl": destUrl})
    data = r.json()
    if r.status_code != 201:
        return await ctx.send(f"Error when creating the URL: {data['Error']}")
    return await ctx.send(
        f"Created `{data['ShortUrl']}` that redirects to `{data['DestUrl']}`"
    )


@url.command()
async def delete(ctx, key: str):
    """
    Take a guess...
    Examples:
        >>> url delete FizzBuzz
    """
    r = requests.delete(API_URL + f"/d/{key}")
    if r.status_code == 404:
        data = r.json()
        return await ctx.send(f"Error when trying to delete `{key}`: {data['Error']}")
    return await ctx.send(f"`{key}` deleted successfully")


async def setup(bot: Bot) -> None:
    bot.add_command(url)
