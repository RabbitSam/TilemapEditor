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
        self.ratio = (1, 1)

    def __deepcopy__(self, memodict={}):
        copy_sprite = Sprite(deepcopy(self._original))
        copy_sprite.sprite = self.sprite
        copy_sprite.set_ratio(self.ratio)

        return copy_sprite

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

    def snap_to_ratio(self):
        """
        Snap the sprite size to its current ratio
        """
        size = self.get_size()
        self.resize((size[0] * self.ratio[0], size[1] * self.ratio[1]))

    def get_photo_image(self):
        """
        Get the photo image of the sprite
        :return: The photo image
        """
        return ImageTk.PhotoImage(self.sprite)

    def get_size(self):
        """
        Get the size of the sprite
        :return: The size of the sprite
        """
        return self.sprite.size

    def rotate(self, angle):
        """
        Rotate the image
        :param angle: The angle to rotate to
        """
        self.sprite = self.sprite.rotate(angle)

    def set_ratio(self, ratio):
        """
        Set the ratio of the sprite
        :param ratio: The ratio to set
        """
        if ratio[0] >= 1 and ratio[1] >= 1:
            self.ratio = ratio

    def get_ratio(self):
        """
        Get the current ratio of the sprite
        :return:
        """
        return self.ratio

    def reset_ratio(self):
        """
        Resets snapping ratio
        """
        self.ratio = (1, 1)

    def get_ghost_photoimage(self):
        """
        Creates an image with reduced alpha and returns its photoimage
        :return: The photoimage with reduced alpha
        """
        ghost = deepcopy(self.sprite)
        ghost.putalpha(100)
        return ImageTk.PhotoImage(ghost)

