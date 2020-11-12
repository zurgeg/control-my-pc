from twitchio.ext.commands.bot import Bot


class TwitchConnection(Bot):
    # TODO: write docstrings
    def __init__(self, user, oauth, user_permissions, client_id=None, prefix=None):
        USER_PERMISSIONS = user_permissions

        if client_id is None:
            client_id = 'CMPCscript (+https://cmpc.live/)'
        if prefix is None:
            # TODO: Change?
            prefix = 'asdf'

        super().__init__(irc_token=oauth, client_id=client_id, nick=user, prefix=prefix, initial_channels=[user])

    # I don't know why this method is classed as necessary to implement but here it is.
    async def event_pubsub(self, data):
        pass
