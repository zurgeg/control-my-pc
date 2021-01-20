import asyncio
import twitchio
import twitchio.dataclasses as dataclasses

class MockUser:
    def __init__(self, name)
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name

class MockMessage:
    def __init__(self, author:MockUser, messageContent:str):
        self._content = messageContent
        self._author = author
    
    @property
    def content(self) -> str:
        return self._content

    @property
    def author(self) -> MockUser:
        return self._author

class ScriptTester(object):
    def __init__ (self, messageCallback):
        self.messageCallback = messageCallback

    async def inputLoop(self):
        while True:
            if not self._user:
                user = input('[Offline Mode] What user would you like to mock?')
                self._author = MockUser(user)

            message = input('[Offline Mode] What message would you like to send?')
            if message = '//switchuser':
                self._user = None
            elif message = '//exit':
                print('[Offline Mode] Use Ctrl-C to exit (Command-C on MacOS)')
            else:
                self._lastMessage = MockMessage(self._author)


    def startTester(self):
        """
        Starts the input loop which makes a mock twitchio message, then sends it to the messageCallback.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self.inputLoop())

        try:
            print('[Offline Mode] Starting Input Loop')
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        print('[Offline Mode] Stopping Asyncio Loop')
        loop.stop()
        loop.close()
        


