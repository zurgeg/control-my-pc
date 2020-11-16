# What is the point of all this? Why not just use simple attributes? -J
class Permissions:
    """Holds the permissions of a user.

    Instance variables:
        moderator
        developer
        script
    """

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
        """Getter for the moderator attribute.

        Finds the boolean of the bitwise AND between the instance's value and MOD_PERMISSION
        Therefore returns True if the instance's permissions value has a 1 in the MOD_PERMISSION position.
        """
        return bool(self.value & self.MOD_PERMISSION)

    @moderator.setter
    def moderator(self, value):
        """Setter for the moderator attribute.

        Args:
            value -- boolean indicating whether the instance has moderator permissions.
        If giving the instance moderator permissions, use a bitwise OR to set a 1 in the MOD_PERMISSION position.
        Otherwise, use a bitwise AND with the bitwise XOR of ALL_PERMISSIONS and MOD_PERMISSION
        to set a 0 in the MOD_PERMISSION position.
        """
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
