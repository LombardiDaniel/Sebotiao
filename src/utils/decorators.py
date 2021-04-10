from secrets import choice

from extras import constants


def admin_only(command_func):
    '''
    Decorator to allow only administrators to call the function.
    This decorator does not raises an error (as is the case with
    "@commands.has_permissions(administrator=True)"). Instead, it
    sends a negative repply to the chat.
    '''
    async def wrap(self, ctx, *args, **kwargs):

        if not ctx.author.guild_permissions.administrator:
            await ctx.message.channel.send("vc n pode pedir isso :joy: :joy: :joy:")
            return

        return await command_func(self, ctx, *args, **kwargs)

    return wrap


def in_voice_chat_only(command_func):
    '''
    Decorator to only call the function if the user (caller) is in a voice chat.
    '''
    async def wrap(self, ctx, *args, **kwargs):

        if not ctx.message.author.voice:
            await ctx.message.channel.send(choice(constants.NEGATIVE_RESPONSES))
            return

        return await command_func(self, ctx, *args, **kwargs)

    return wrap


# def no_bots(main_func):
#     '''
#     Decorator to block bots from calling function.
#     '''
#     async def wrap(self, *args, **kwargs):
#
#         if args.message.author.bot:
#             return
#
#         return await main_func(self, ctx, *args, **kwargs)
#
#     return wrap
