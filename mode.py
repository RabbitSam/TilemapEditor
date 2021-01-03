from enum import Enum, auto


class Modes(Enum):
    DEFAULT = auto()
    DRAG = auto()
    ZOOM = auto()
    ADD = auto()
    EDIT = auto()
    DELETE = auto()


class ModeCursors(Enum):
    DEFAULT = "arrow"
    DRAG = "fleur"
    ZOOM = "arrow"
    ADD = "plus"
    EDIT = "hand2"
    DELETE = "X_cursor"


class Mode:
    def __init__(self):
        """
        Creates a mode instance with default mode.
        """
        self.mode = Modes.DEFAULT
        self._archived_mode = None
        # If a mode has a related item, it will be here.
        # Might change to array or dict if needed in the future.
        self.related_item = None
        self._archived_related_item = None

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
        """
        Returns the mode value

        :return: The value of the mode
        """
        return self.mode

    def in_default_mode(self):
        """
        Returns whether the current mode is default or not

        :return: True if the current mode is default, false otherwise
        """
        return self.mode == Modes.DEFAULT

    def archive_mode(self):
        """
        Archives the current mode
        """
        if self._archived_mode is None:
            self._archived_mode = self.mode
            self._archived_related_item = self.related_item

    def unarchive_mode(self):
        """
        Unarchives the archived mode
        """
        self.mode, self._archived_mode = self._archived_mode, None
        self.related_item, self._archived_related_item = self._archived_related_item, None

    # ------------------------------------------------ ITEM METHODS -------------------------------------------- #
    def set_related_item(self, item):
        """
        Set the related item to the related item

        :param item: The item to set
        """
        self.related_item = item

    def reset_related_item(self):
        """
        Reset the related item
        """
        self.set_related_item(None)

    def has_related_item(self):
        """
        Checks if there is a related item
        :return: True if there is a related item, False otherwise.
        """
        return self.related_item is not None

    def get_related_item(self):
        """
        Returns the related item
        :return: The related item
        """
        return self.related_item

    # ------------------------------------ Cursor methods ---------------------------------- #
    def get_cursor(self):
        return ModeCursors[self.mode.name].value



