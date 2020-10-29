import tkinter as tk
from PIL import ImageTk


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

        self.create_canvas()

    def create_canvas(self):
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
        photo_image_sprite = ImageTk.PhotoImage(sprite.sprite)

        # Create the image
        image_id = self.canvas.create_image((0, len(self.images) * 55), image=photo_image_sprite)
        self.canvas.images.append(photo_image_sprite)
        self.images.append((image_id, sprite))
        print(image_id)

        # Set scroll region
        bbox = self.canvas.bbox(tk.ALL)
        self.canvas.configure(scrollregion=bbox)

        # Adjust height
        new_height = bbox[3] - bbox[1]
        self.canvas.configure(height=new_height)


