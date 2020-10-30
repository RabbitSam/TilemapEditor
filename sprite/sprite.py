from PIL import Image, ImageTk


class Sprite:
    def __init__(self, image: Image):
        """
        Sprite class, keeps an original and a copy. This allows the sprite to be resized without breaking
        the image. Of course the image will still break if scaled above its original size.

        :param image: The image to be turned into a sprite
        """
        self._original = image
        self.sprite = image

    def resize(self, size: tuple):
        """
        Resize the sprite.

        :param size: The size, (width, height).
        """
        self.sprite = self._original.resize(size)

    def get_photo_image(self):
        return ImageTk.PhotoImage(self.sprite)
