import tkinter as tk
from PIL import ImageTk
from mode import Modes


class TileMenu(tk.Frame):
    def __init__(self, master=None, mode=None, width=50, height=50):
        """
        Create the tile_menu

        :param master: The master object
        :param mode: The mode object
        """
        super().__init__(master=master, width=width, height=height)
        self.mode = mode

        # Widgets
        self.canvas = None
        self.yscrollbar = None

        # Size
        self.tile_size = 50

        # Images
        self.images = []

        self._create_canvas()

    def _create_canvas(self):
        """
        Create the  canvas and the scroll region
        """
        # Create the canvas
        self.canvas = tk.Canvas(master=self, width=self.tile_size, height=self.tile_size,
                                scrollregion=(0, 0, self.tile_size, self.tile_size))
        self.canvas.configure(bg="grey")
        self.canvas.images = []

        # YScrollbar
        self.yscrollbar = tk.Scrollbar(master=self, orient=tk.VERTICAL)
        self.yscrollbar.config(command=self.canvas.yview)
        self.yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.config(yscrollcommand=self.yscrollbar.set)
        self.canvas.pack()

    def add_sprite(self, sprite):
        """
        Adds a sprite to the tile_menu

        :param sprite: The sprite to add
        """
        # Resize the image
        sprite.resize((self.tile_size, self.tile_size))
        photo_image_sprite = sprite.get_photo_image()

        # Create the image
        image_id = self.canvas.create_image((0, len(self.images) * (self.tile_size + 5)), image=photo_image_sprite)
        self.canvas.images.append(photo_image_sprite)
        self.images.append((image_id, sprite))

        # Set tile click event
        self.canvas.tag_bind(image_id, "<Button-1>", lambda _: self._set_related_item(sprite))

        # Set scroll region
        bbox = self.canvas.bbox(tk.ALL)
        self.canvas.configure(scrollregion=bbox)

        # Adjust height
        new_height = bbox[3] - bbox[1]
        self.canvas.configure(height=new_height)

    def _set_related_item(self, sprite):
        """
        Sets the sprite as a related item for the mode.

        :param sprite: The sprite to set
        """
        # Only if the mode is add, then set the related_item
        if self.mode == Modes.ADD:
            self.mode.set_related_item(sprite)



