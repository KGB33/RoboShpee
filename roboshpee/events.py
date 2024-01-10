import re

import discord


async def on_twitter_msg(msg: discord.Message, matches: list[str]):
    reply = "\n".join(
        re.sub(
            r"https?://(?:vxtwitter|twitter|x)\.com/([^.\s]+)", r"https://nitter.net/\1", match
        )
        for match in matches
    )
    await msg.reply(reply, mention_author=False)
