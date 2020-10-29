import tkinter as tk
from tkinter import filedialog
from PIL import Image
from sprite.sprite import Sprite


class Menu(tk.Frame):
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

        self.create_widgets()

    def create_widgets(self):
        """
        Create the buttons to perform different functionality.
        """
        button_import = tk.Button(master=self, text="Import Sprite", command=self.import_sprite)
        button_import.grid(row=0, column=0)

        # TODO: Mode buttons

    def import_sprite(self):
        """
        Import a sprite and render it on the tile menu
        """
        filename = filedialog.askopenfilename()
        if filename != "":
            # Load image, store into sprite class, add to tile menu
            image = Image.open(filename)
            sprite = Sprite(image)
            self.tile_menu.add_sprite(sprite)
