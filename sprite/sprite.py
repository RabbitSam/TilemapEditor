from PIL import Image, ImageTk
from copy import deepcopy


class Sprite:
    def __init__(self, image: Image):
        """
        Sprite class, keeps an original and a copy. This allows the sprite to be resized without breaking
        the image. Of course the image will still break if scaled above its original size.

        :param image: The image to be turned into a sprite
        """
        self._original = image
        self.sprite = image
        self.rotation = 0

    def __deepcopy__(self, memodict={}):
        return Sprite(deepcopy(self._original))

    def resize(self, size: tuple):
        """
        Resize the sprite.

        :param size: The size, (width, height).
        """
        self.sprite = self._original.resize(size)

    def get_photo_image(self):
        return ImageTk.PhotoImage(self.sprite)

    def get_size(self):
        return self.sprite.size

    def rotate(self, angle):
        self.sprite = self.sprite.rotate(angle)
