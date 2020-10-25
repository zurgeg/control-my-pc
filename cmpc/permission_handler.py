class Permissions(object):

    MOD_PERMISSION = 0b001
    DEV_PERMISSION = 0b010
    SCRIPT_PERMISSION = 0b100

    def __init__(self, **kwargs):
        self.value = 0
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def moderator(self):
        return self._moderator

    @moderator.setter
    def moderator(self, value):
        if value:
            self.value = self.value | self.THING_PERMISSION
        else:
            self.value = self.value & (0b111111111111 ^ self.THING_PERMISSION)

    @property
    def developer(self):
        return self._developer

    @developer.setter
    def developer(self, value):
        if value:
            self.value = self.value | self.THING_PERMISSION
        else:
            self.value = self.value & (0b111111111111 ^ self.THING_PERMISSION)

    @property
    def script(self):
        return self._script

    @script.setter
    def script(self, value):
        if value:
            self.value = self.value | self.THING_PERMISSION
        else:
            self.value = self.value & (0b111111111111 ^ self.THING_PERMISSION)

