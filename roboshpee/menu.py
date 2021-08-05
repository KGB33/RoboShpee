import asyncio
import inspect
from typing import Callable

import discord


class ReactionMenu:
    @classmethod
    async def create(
        cls,
        ctx,
        msg: discord.Message,
        body: str,
        options: dict[str, "ReactionMenuOption"],
    ):
        obj = ReactionMenu(ctx, msg, body, options)
        await obj._populate_msg()
        return obj

    def __init__(
        self,
        ctx,
        msg: discord.Message,
        body: str,
        options: dict[str, "ReactionMenuOption"],
    ):
        self.ctx = ctx
        self.msg = msg
        self.body = body
        self.options = options
        self.compleated = False

    async def _populate_msg(self):
        """
        A post init function to populate the body of the message
        and to react to it with the needed emoji
        """
        await self.msg.edit(content=self.body)
        for emoji in self.options.keys():
            await self.msg.add_reaction(emoji)

    async def wait_for_results(self):
        while not self.compleated:
            reaction_group = {
                asyncio.create_task(
                    self.ctx.bot.wait_for(
                        "raw_reaction_add", check=self._reaction_check
                    )
                ),
                asyncio.create_task(
                    self.ctx.bot.wait_for(
                        "raw_reaction_remove", check=self._reaction_check
                    )
                ),
            }
            finished, _ = await asyncio.wait(
                reaction_group, return_when=asyncio.FIRST_COMPLETED
            )
            reaction = list(finished)[0].result()
            if await self.options[str(reaction.emoji)].handle_reaction_event(reaction):
                break
        await self._handle_results()

    async def _handle_results(self):
        await self.msg.clear_reactions()
        for option in self.options.values():
            if option.activated:
                if inspect.iscoroutinefunction(option.callback_func):
                    await option.callback_func()
                else:
                    option.callback_func()

    def _reaction_check(self, r: discord.RawReactionActionEvent) -> bool:
        if r.user_id == self.ctx.bot.user.id:
            return False
        if r.message_id != self.msg.id:
            return False
        if str(r.emoji) not in self.options.keys():
            return False
        return True


class ReactionMenuOption:
    def __init__(
        self,
        callback_func: Callable,
        on_reaction_add: Callable = lambda *args, **kwargs: None,
        on_reaction_remove: Callable = lambda *args, **kwargs: None,
        calculate_reaction_value: Callable = lambda *args, **kwargs: 1,
        callback_trigger: int = 1,
    ):
        self.callback_func = callback_func
        self.on_reaction_add = on_reaction_add
        self.on_reaction_remove = on_reaction_remove
        self._callback_trigger = callback_trigger
        self._calculate_reaction_value_func = calculate_reaction_value
        self.state = 0

    @property
    def activated(self) -> bool:
        return self.state >= self._callback_trigger

    async def handle_reaction_event(self, r: discord.RawReactionActionEvent) -> bool:
        if r.event_type == "REACTION_ADD":
            return await self._reaction_add(r)
        return await self._reaction_remove(r)

    async def _reaction_add(self, r: discord.RawReactionActionEvent) -> bool:
        self.state += await self._calculate_reaction_value(r)

        if inspect.iscoroutinefunction(self.on_reaction_add):
            await self.on_reaction_add(self)
        else:
            self.on_reaction_add(self)

        return self.activated

    async def _reaction_remove(self, r: discord.RawReactionActionEvent) -> bool:
        self.state -= await self._calculate_reaction_value(r)

        if inspect.iscoroutinefunction(self.on_reaction_remove):
            await self.on_reaction_remove(self)
        else:
            self.on_reaction_remove(self)

        return self.activated

    async def _calculate_reaction_value(self, r) -> int:
        if inspect.iscoroutinefunction(self._calculate_reaction_value_func):
            return await self._calculate_reaction_value_func(r)
        else:
            return self._calculate_reaction_value_func(r)
