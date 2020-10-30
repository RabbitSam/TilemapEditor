from enum import Enum, auto


class Modes(Enum):
    DEFAULT = auto()
    DRAG = auto()
    ZOOM = auto()
    ADD = auto()


class Mode:
    def __init__(self):
        """
        Creates a mode instance with default mode.
        """
        self.mode = Modes.DEFAULT
        # If a mode has a related item, it will be here.
        # Might change to array or dict if needed in the future.
        self.related_item = None

    # ----------------------------------------------- BUILT-INS ------------------------------------------------ #
    def __eq__(self, other):
        """
        If you want to check what the current mode is

        :param other: The mode to check against.
        :return: True if equal, False otherwise
        """
        return self.mode == other

    # ------------------------------------------------ MODE METHODS -------------------------------------------- #
    def set_mode(self, mode):
        """
        Change the mode. MUST BE IN MODES ENUM.

        :param mode: The mode to change to
        """
        if mode in Modes:
            self.mode = mode

    def reset_mode(self):
        """
        Resets mode to default
        """
        self.set_mode(Modes.DEFAULT)
        self.reset_related_item()

    def get_mode_value(self):
        return self.mode

    def in_default_mode(self):
        return self.mode == Modes.DEFAULT

    # ------------------------------------------------ ITEM METHODS -------------------------------------------- #
    def set_related_item(self, item):
        self.related_item = item

    def reset_related_item(self):
        self.set_related_item(None)

    def has_related_item(self):
        return self.related_item is not None

    def get_related_item(self):
        return self.related_item



