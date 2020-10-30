import tkinter as tk
import math
from mode import Modes
from PIL import ImageTk


class InfiniteCanvas(tk.Frame):
    def __init__(self, master=None, mode=None, width: int = 50, height: int = 50):
        """
        Initializes an infinite canvas that can be drag scrolled.

        :param master: The master holding the frame.
        :param width: The width of the frame.
        :param height: The height of the frame.
        """
        # Super class init
        super().__init__(master=master, width=width, height=height)

        # Frame children
        self._canvas = None
        self._canvas_xscrollbar = None
        self._canvas_yscrollbar = None

        # Canvas grid size
        self._grid_size = 50

        # Canvas width and height
        self._cwidth = self.winfo_screenwidth() * 2
        self._cheight = self.winfo_screenheight() * 2

        # Frame data
        self._width = width
        self._height = height

        # Instance data
        # Modes
        self._mode = mode

        # Dragging variables
        self._drag_src_coords = (-1, -1)  # (x, y)

        # Grids
        self._canvas_grid = []

        # Create canvas
        self._create_canvas()
        self._create_canvas_events()
        self._create_canvas_grid()

    # ------------------------------------ Events --------------------------------------- #
    def _handle_button_motion(self, event):
        """
        Handle button motion events.
        Use this for mouse drag events (eg. Drag scrolling, drag moving items in the canvas, ..)

        :param event: The tkinter event.
        """
        # If the current mode is drag
        if self._mode == Modes.DRAG:
            # If there is no original source coordinates, set them this round and start dragging next round.
            if self._drag_src_coords == (-1, -1):
                self._drag_src_coords = (event.x, event.y)
            else:
                # Calculate how much to move the area
                xdiff = math.floor(self._drag_src_coords[0] - event.x)
                ydiff = math.floor(self._drag_src_coords[1] - event.y)

                # Set scroll increment
                self._canvas.config(yscrollincrement=1, xscrollincrement=1)

                # Scroll the canvas
                self._canvas.xview_scroll(xdiff, "units")
                self._canvas.yview_scroll(ydiff, "units")

                # Set old location as the current location
                self._drag_src_coords = (event.x, event.y)

    def _handle_button_release(self, event):
        """
        Handle button release events.
        Use primarily to reset button release.

        :param event: The tkinter event.
        """
        if self._mode == Modes.DRAG:
            self._drag_src_coords = (-1, -1)
            self._canvas.config(yscrollincrement=0, xscrollincrement=0)

    def _handle_zoom(self, event):
        """
        Handles zoom related events.

        :param event: The tkinter event.
        :return:
        """
        if self._mode == Modes.ZOOM:
            scale_factor = 1.001 ** event.delta     # The amount to scale by

            # Scale the page and set the scroll region to within the bbox
            self._canvas.scale(tk.ALL, event.x, event.y, scale_factor, scale_factor)
            self._canvas.config(scrollregion=self._canvas.bbox(tk.ALL))

    # ------------------------- Mode Events ----------------------------- #
    # The methods below should be replaced by direct calls to the mode instance methods
    # At the moment however, it's fine.
    # I can fix this later.
    def _in_default_mode(self):
        """
        Checks if the mode is default.

        :return: Boolean indicating if the mode is default. True if default, False otherwise.
        """
        return self._mode.in_default_mode()

    def _set_mode(self, mode):
        """
        Set the mode to some other mode

        :param mode: The mode to set.
        """
        self._mode.set_mode(mode)

    def _reset_mode(self):
        """
        Reset the mode to default.
        """
        self._mode.reset_mode()

    # The methods below this should stay the same however.
    def _set_drag_mode(self, event):
        """
        Set Drag Mode. Used to enable and disable drag events.

        :param event: The tkinter event
        """
        # Check whether to activate or deactivate the drag event
        if str(event.type) == "KeyPress" and self._in_default_mode():
            self._set_mode(Modes.DRAG)
            self._canvas.config(cursor="fleur")
        elif str(event.type) == "KeyRelease":
            # Reset Drag variables
            self._reset_mode()
            self._drag_src_coords = (-1, -1)
            self._canvas.config(cursor="arrow")

    def _set_zoom_mode(self, event):
        """
        Set Drag Mode. Used to enable and disable drag events.

        :param event: The tkinter event
        """
        # Check whether to activate or deactivate the zoom event
        if str(event.type) == "KeyPress" and self._in_default_mode():
            self._set_mode(Modes.ZOOM)
        elif str(event.type) == "KeyRelease":
            # Reset Zoom variables
            self._reset_mode()

    def _set_current_mode(self, event):
        """
        Set the current mode

        :param event: The tkinter event
        """
        if str(event.type) == "Enter":
            if self._mode == Modes.ADD:
                self._canvas.config(cursor="cross")
        elif str(event.type) == "Leave":
            self._canvas.config(cursor="arrow")

    def _clicked(self, event):
        if self._mode == Modes.ADD and self._mode.has_related_item():
            sprite = self._mode.get_related_item()

            # Calculate coords
            canvasx = self._canvas.canvasx(event.x)
            canvasy = self._canvas.canvasy(event.y)
            bbox = self._canvas.bbox(self._canvas.find_closest(canvasx, canvasy))
            coords = bbox[0], bbox[1]

            # Get the width and height
            bbox = self._canvas.bbox("ref_rect")
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]

            # Resize the sprite
            sprite.resize((width, height))
            photo_image_sprite = sprite.get_photo_image()

            self._canvas.create_image(coords[0], coords[1], image=photo_image_sprite, anchor="nw")
            self._canvas.placed_images.append(photo_image_sprite)

    # ----------------------------------- canvas Method ------------------------------------ #
    def _create_canvas(self):
        """
        Create and pack the canvas.
        """
        # Create a  canvas with double the width and double the height so that the user has more room to work with
        self._canvas = tk.Canvas(master=self, width=self._cwidth, height=self._cheight,
                                 scrollregion=(0, 0, self._cwidth, self._cheight), confine=True)
        self._canvas.configure(bg="grey")    # To see if it is being rendered correctly
        self._canvas.placed_images = []

        # XScrollbar
        self._canvas_xscrollbar = tk.Scrollbar(master=self, orient=tk.HORIZONTAL)
        self._canvas_xscrollbar.config(command=self._canvas.xview)

        # YScrollbar
        self._canvas_yscrollbar = tk.Scrollbar(master=self, orient=tk.VERTICAL)
        self._canvas_yscrollbar.config(command=self._canvas.yview)

        # Pack
        self._canvas_xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self._canvas_yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack canvas
        self._canvas.config(xscrollcommand=self._canvas_xscrollbar.set, yscrollcommand=self._canvas_yscrollbar.set)
        self._canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self._canvas.focus_set()

    def _create_canvas_events(self):
        """
        Create canvas events. Used to bind events to the canvas widget.
        """
        # Create events for the canvas
        # Mouse Drag and release
        self._canvas.bind("<B1-Motion>", self._handle_button_motion)
        self._canvas.bind("<ButtonRelease-1>", self._handle_button_release)

        # Mouse Scroll
        self._canvas.bind("<MouseWheel>", self._handle_zoom)

        # Drag mode
        self._canvas.bind("<KeyPress-space>", self._set_drag_mode)
        self._canvas.bind("<KeyRelease-space>", self._set_drag_mode)

        # Zoom mode
        self._canvas.bind("<KeyPress-Control_L>", self._set_zoom_mode)
        self._canvas.bind("<KeyRelease-Control_L>", self._set_zoom_mode)

        # Add mode
        self._canvas.bind("<Enter>", self._set_current_mode)
        self._canvas.bind("<Leave>", self._set_current_mode)

        # Mouse Click Events
        self._canvas.bind("<Button-1>", self._clicked)

    def _create_canvas_grid(self):
        """
        Create canvas grid. Used to generate the grid on the canvas.
        """
        # Create the grid
        for x1 in range(0, self._cwidth - self._grid_size, self._grid_size):
            x2 = x1 + self._grid_size
            for y1 in range(0, self._cheight - self._grid_size, self._grid_size):
                y2 = y1 + self._grid_size
                rect_id = self._canvas.create_rectangle(x1, y1, x2, y2, fill="grey")
                if (x1, y1) == (0, 0):
                    self._canvas.addtag_withtag("ref_rect", rect_id)

        # Set scroll region within the confines of the grid
        self._canvas.config(scrollregion=self._canvas.bbox(tk.ALL))


