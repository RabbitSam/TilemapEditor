import tkinter as tk


class CanvasImage(tk.Label):
    def __init__(self, master=None, sprite=None, width=None, height=None):
        """
        Create a canvas image.

        :param master: The master frame
        :param sprite: The sprite
        :param width: The width
        :param height: The height
        """
        # Image Variables
        self.sprite = sprite
        sprite.resize((width, height))
        self.editing = False
        self.ratio = (1, 1)

        # Initialize the image label
        photo_image_sprite = self.sprite.get_photo_image()
        super().__init__(master=master, image=photo_image_sprite, borderwidth=0)
        self.image = photo_image_sprite

    def zoom_image(self, grid_size):
        """
        Resizes the image
        """
        # Resize the image only if it is viewable and if the photoimage isn't the same size
        if self.winfo_viewable() and\
                (self.image.width(), self.image.height()) != (grid_size * self.ratio[0], grid_size * self.ratio[1]):
            # Resize the sprite.
            self.sprite.resize((grid_size * self.ratio[0], grid_size * self.ratio[1]))

            # Replace the image
            photo_image_sprite = self.sprite.get_photo_image()
            self.configure(image=photo_image_sprite)
            self.image = photo_image_sprite

