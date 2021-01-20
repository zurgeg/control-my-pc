import asyncio

class ScriptTester(object):
    def __init__ (self, messageCallback):
        self.messageCallback = messageCallback
        self.loop = asyncio.loop

    def startTester(self):
        pass

