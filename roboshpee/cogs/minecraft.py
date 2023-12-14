from discord.ext import commands
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from textwrap import dedent

from roboshpee.bot import Bot


@commands.hybrid_command()
async def minecraft(ctx):
    status = (await _fetch_status())["docker"]["ps"]
    for server in status:
        await ctx.send(
            dedent(
                f"""
                The server (`{server['names']}`) is `{server['state']}` and has been `{server['status']}`.
                """
            )
        )


async def _fetch_status():
    transport = AIOHTTPTransport(url="http://10.0.9.120:4807/graphql")

    async with Client(
        transport=transport,
        fetch_schema_from_transport=True,
    ) as session:
        query = gql(
            """
            {
              docker {
                ps {
                  names
                  state
                  status
                }
              }
            }
            """
        )

        return await session.execute(query)


async def setup(bot: Bot) -> None:
    bot.add_command(minecraft)
