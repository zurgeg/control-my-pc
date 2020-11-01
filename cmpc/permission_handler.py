class Permissions:

    MOD_PERMISSION = 0b001
    DEV_PERMISSION = 0b010
    SCRIPT_PERMISSION = 0b100

    ALL_PERMISSIONS = 0b111111111111  # This doesn't need to be accurate it just needs to be bigger than everything else

    def __init__(self, **kwargs):
        """Initialise the class attributes, including keyword arguments."""
        self.value = 0
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def moderator(self):
        return bool(self.value & self.MOD_PERMISSION)

    @moderator.setter
    def moderator(self, value):
        if value:
            self.value = self.value | self.MOD_PERMISSION
        else:
            self.value = self.value & (self.ALL_PERMISSIONS ^ self.MOD_PERMISSION)

    @property
    def developer(self):
        return bool(self.value & self.DEV_PERMISSION)

    @developer.setter
    def developer(self, value):
        if value:
            self.value = self.value | self.DEV_PERMISSION
        else:
            self.value = self.value & (self.ALL_PERMISSIONS ^ self.DEV_PERMISSION)

    @property
    def script(self):
        return bool(self.value & self.SCRIPT_PERMISSION)

    @script.setter
    def script(self, value):
        if value:
            self.value = self.value | self.SCRIPT_PERMISSION
        else:
            self.value = self.value & (self.ALL_PERMISSIONS ^ self.SCRIPT_PERMISSION)
