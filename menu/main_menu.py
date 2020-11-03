import tkinter as tk
from tkinter import filedialog
from PIL import Image
from sprite.sprite import Sprite
from mode import Modes


class MainMenu(tk.Frame):
    def __init__(self, master=None, mode=None, tile_menu=None):
        """
        Menu. Creates the menu with buttons for importing sprites and setting modes.

        :param master: The master container
        :param mode: The mode object
        :param tile_menu: The tile menu object
        """
        super().__init__(master=master)
        self.mode = mode
        self.tile_menu = tile_menu

        self._create_widgets()

    def _create_widgets(self):
        """
        Create the buttons to perform different functionality.
        """
        button_import = tk.Button(master=self, text="Import Sprite", command=self._import_sprite)
        button_import.grid(row=0, column=0, sticky="WE")

        button_add = tk.Button(master=self, text="Add Sprite", command=self._add_sprite)
        button_add.grid(row=1, column=0, sticky="WE")

    def _import_sprite(self):
        """
        Import a sprite and render it on the tile menu
        """
        filename = filedialog.askopenfilename()
        if filename != "":
            # Load image, store into sprite class, add to tile menu
            image = Image.open(filename)
            sprite = Sprite(image)
            self.tile_menu.add_sprite(sprite)

    def _add_sprite(self):
        """
        Set the mode to add sprite
        """
        self.mode.set_mode(Modes.ADD)
