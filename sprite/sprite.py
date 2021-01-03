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
        self.ratio = (1, 1)

    def __deepcopy__(self, memodict={}):
        return Sprite(deepcopy(self._original))

    def resize(self, size: tuple):
        """
        Resize the sprite.

        :param size: The size, (width, height).
        """
        size = list(size)
        sprite_size = self.get_size()
        if size[0] <= 0:
            size[0] = sprite_size[0]
        if size[1] <= 0:
            size[1] = sprite_size[1]

        final_size = size
        self.sprite = self._original.resize(tuple(final_size))

    def snap_to_ratio(self, size):
        self.resize((size[0] * self.ratio[0], size[1] * self.ratio[1]))

    def get_photo_image(self):
        return ImageTk.PhotoImage(self.sprite)

    def get_size(self):
        return self.sprite.size

    def rotate(self, angle):
        self.sprite = self.sprite.rotate(angle)

    def set_ratio(self, ratio):
        if ratio[0] >= 1 and ratio[1] >= 1:
            self.ratio = ratio

    def get_ratio(self):
        return self.ratio

    def reset_ratio(self):
        self.ratio = (1, 1)
