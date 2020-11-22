"""Features superclass that uses twitchio to connect to Twitch.

Classes:
    TwitchConnection -- Parent class for TwitchPlays class
"""

from twitchio.ext.commands.bot import Bot


class TwitchConnection(Bot):
    """A layer on the twitchio.ext.commands.bot.Bot class to better fit how we use it.

    Instance variables:
        user -- the Twitch channel to log into and monitor chat
                equivalent to twitchio nick
        oauth -- the key to use to log into Twitch
                 equivalent to twitchio irc_token
        client_id -- twitchio client_id
        initial_channels -- the channels to join, may be None in which case it will default to just the user
        prefix -- twitchio prefix, defaults to asdf as unused
    """

    def __init__(self, user, oauth, client_id, initial_channels, prefix=None):
        """Extend Bot.__init__, makes prefix optional and sets initial_channels to a list containing nick by default."""
        if prefix is None:
            prefix = '!'
        if initial_channels is None:
            initial_channels = [user]

        super().__init__(irc_token=oauth, client_id=client_id, nick=user,
                         prefix=prefix, initial_channels=initial_channels)

    # I don't know why this method is classed as necessary to implement but here it is.
    async def event_pubsub(self, data):
        """Override Bot.event_pubsub - do nothing (:."""
        pass
