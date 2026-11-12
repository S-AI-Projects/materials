class LowerString(str):
    """Create a string subclass containing lowercase text."""

    def __new__(cls, string):
        return super().__new__(cls, string.lower())
