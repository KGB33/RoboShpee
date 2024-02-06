from textwrap import dedent

from discord.ext import commands
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from roboshpee.bot import Bot


@commands.hybrid_command()
async def minecraft(ctx):
    resp = await _fetch_status()
    match resp:
        # {'docker': {'ps': status}, 'disk': {'usage': [{'usePercent': 61}]}}
        case {
            "docker": {"ps": status},
            "disk": {"usage": [{"usePercent": use_percent}]},
        }:
            pass
        case _:
            await ctx.send("Could not process response")
            print(resp)
            return
    out = "\n".join(
        dedent(
            f"""
                The server (`{server['names']}`) is `{server['state']}` and has been `{server['status']}`.
                """
        )
        for server in status
    )
    await ctx.send(f"{out}`{use_percent}%` disk space has been used.")


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
              disk {
                usage(path: "/") {
                  usePercent
                }
              }
            }
            """
        )

        return await session.execute(query)


async def setup(bot: Bot) -> None:
    bot.add_command(minecraft)
