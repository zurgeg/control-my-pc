import asyncio


class MockUser:
    def __init__(self, name, id: int = 0):
        self.name = name
        self.id = id


class MockMessage:
    def __init__(self, author: MockUser, content: str):
        self.content = content
        self.author = author


class ScriptTester(object):
    def __init__(self, messageCallback, originalSelf):
        self.message_callback = messageCallback
        self._user = None
        self._original_self = originalSelf
        self._last_message = None

    async def input_loop(self):
        while True:
            if self._user is None:
                user = input('[Offline Mode] What user would you like to mock?')
                userid = input('[Offline Mode] What user ID would you like to use? '
                               "(If you don't know what this is, use 0)")
                if userid:
                    self._author = MockUser(user, userid)
                else:
                    self._author = MockUser(user)

            message = input('[Offline Mode] What message would you like to send?')
            if message == '//switchuser':
                self._user = None
            elif message == '//exit':
                print('[Offline Mode] Use Ctrl-C to exit (Command-C on MacOS)')
            else:
                self._last_message = MockMessage(self._author, message)
                await self.message_callback(self=self._original_self, message=self._last_message)

    def run(self):
        """Starts the input loop which makes a mock twitchio message, then sends it to the messageCallback."""
        loop = asyncio.get_event_loop()
        loop.create_task(self.input_loop())

        try:
            print('[Offline Mode] Starting Input Loop')
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        print('[Offline Mode] Stopping Asyncio Loop')
        loop.stop()
        loop.close()

