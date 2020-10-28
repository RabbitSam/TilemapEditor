import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTK


class Menu(tk.Frame):
    def __init__(self, master=None, mode=None, tile_menu=None):
        super().__init__(master=master)
        self.mode = mode
        self.tile_menu = tile_menu

        self.create_widgets()

    def create_widgets(self):
        button_import = tk.Button(master=self, text="Import Sprite", command=self.import_sprite)
        button_import.grid(row=0, column=0)

    def import_sprite(self):
        sprite = filedialog.askopenfilename()
        if sprite is not None:
            # Load the sprite
            # Create a copy of the sprite
            # Resize the copy, keep the original
            # Put them into the item_menu
            pass
