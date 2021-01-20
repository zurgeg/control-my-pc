import asyncio

class ScriptTester(object):
    def __init__ (self, messageCallback):
        self.messageCallback = messageCallback
        self.loop = asyncio.loop

    async def inputLoop(self):


    def startTester(self):
        """
        Starts the input loop which makes a mock twitchio message, then sends it to the messageCallback.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self.inputLoop)

        try:
            print("[Offline Mode] Starting Input Loop")
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        print()
        


