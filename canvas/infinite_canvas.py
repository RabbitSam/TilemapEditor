import tkinter as tk
import math
from mode import Modes


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
        self.canvas = None
        self.canvas_xscrollbar = None
        self.canvas_yscrollbar = None
        self.grid_size = 50

        # Frame data
        self.width = width
        self.height = height

        # Instance data
        # Modes
        self.mode = mode

        # Dragging variables
        self.drag_src_coords = (-1, -1)  # (x, y)

        # Grids
        self.canvas_grid = []

        # Create canvas
        self.create_canvas()
        self.create_canvas_events()
        self.create_canvas_grid()

    # ------------------------------------ Events --------------------------------------- #
    def __handle_button_motion(self, event):
        """
        Handle button motion events.
        Use this for mouse drag events (eg. Drag scrolling, drag moving items in the canvas, ..)

        :param event: The tkinter event.
        """
        # If the current mode is drag
        if self.mode == Modes.DRAG:
            # If there is no original source coordinates, set them this round and start dragging next round.
            if self.drag_src_coords == (-1, -1):
                self.drag_src_coords = (event.x, event.y)
            else:
                # Calculate how much to move the area
                xdiff = math.floor(self.drag_src_coords[0] - event.x)
                ydiff = math.floor(self.drag_src_coords[1] - event.y)

                # Set scroll increment
                self.canvas.config(yscrollincrement=1, xscrollincrement=1)

                # Scroll the canvas
                self.canvas.xview_scroll(xdiff, "units")
                self.canvas.yview_scroll(ydiff, "units")

                # Set old location as the current location
                self.drag_src_coords = (event.x, event.y)

    def __handle_button_release(self, event):
        """
        Handle button release events.
        Use primarily to reset button release.

        :param event: The tkinter event.
        """
        if self.mode == Modes.DRAG:
            self.drag_src_coords = (-1, -1)
            self.canvas.config(yscrollincrement=0, xscrollincrement=0)

    def __handle_zoom(self, event):
        """
        Handles zoom related events.

        :param event: The tkinter event.
        :return:
        """
        if self.mode == Modes.ZOOM:
            scale_factor = 1.001 ** event.delta     # The amount to scale by

            # Scale the page and set the scroll region to within the bbox
            self.canvas.scale(tk.ALL, event.x, event.y, scale_factor, scale_factor)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    # ------------------------- Mode Events ----------------------------- #
    # The methods below should be replaced by direct calls to the mode instance methods
    # At the moment however, it's fine.
    # I can fix this later.
    def __in_default_mode(self):
        """
        Checks if the mode is default.

        :return: Boolean indicating if the mode is default. True if default, False otherwise.
        """
        return self.mode.in_default_mode()

    def __set_mode(self, mode):
        """
        Set the mode to some other mode

        :param mode: The mode to set.
        """
        self.mode.set_mode(mode)

    def __reset_mode(self):
        """
        Reset the mode to default.
        """
        self.mode.reset_mode()

    # The methods below this should stay the same however.
    def __set_drag_mode(self, event):
        """
        Set Drag Mode. Used to enable and disable drag events.

        :param event: The tkinter event
        """
        # Check whether to activate or deactivate the drag event
        if str(event.type) == "KeyPress" and self.__in_default_mode():
            self.__set_mode(Modes.DRAG)
            self.canvas.config(cursor="fleur")
        elif str(event.type) == "KeyRelease":
            # Reset Drag variables
            self.__reset_mode()
            self.drag_src_coords = (-1, -1)
            self.canvas.config(cursor="arrow")

    def __set_zoom_mode(self, event):
        """
        Set Drag Mode. Used to enable and disable drag events.

        :param event: The tkinter event
        """
        # Check whether to activate or deactivate the zoom event
        if str(event.type) == "KeyPress" and self.__in_default_mode():
            self.__set_mode(Modes.ZOOM)
        elif str(event.type) == "KeyRelease":
            # Reset Zoom variables
            self.__reset_mode()

    # ----------------------------------- canvas Method ------------------------------------ #
    def create_canvas(self):
        """
        Create and pack the canvas.
        """
        # Create a  canvas with double the width and double the height so that the user has more room to work with
        cwidth = self.winfo_screenwidth() * 2
        cheight = self.winfo_screenheight() * 2
        self.canvas = tk.Canvas(master=self, width=cwidth, height=cheight,
                                scrollregion=(0, 0, cwidth, cheight), confine=True)
        self.canvas.configure(bg="grey")    # To see if it is being rendered correctly

        # XScrollbar
        self.canvas_xscrollbar = tk.Scrollbar(master=self, orient=tk.HORIZONTAL)
        self.canvas_xscrollbar.config(command=self.canvas.xview)

        # YScrollbar
        self.canvas_yscrollbar = tk.Scrollbar(master=self, orient=tk.VERTICAL)
        self.canvas_yscrollbar.config(command=self.canvas.yview)

        # Pack
        self.canvas_xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack canvas
        self.canvas.config(xscrollcommand=self.canvas_xscrollbar.set, yscrollcommand=self.canvas_yscrollbar.set)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.canvas.focus_set()

    def create_canvas_events(self):
        """
        Create canvas events. Used to bind events to the canvas widget.
        """
        # Create events for the canvas
        # Mouse Drag and release
        self.canvas.bind("<B1-Motion>", self.__handle_button_motion)
        self.canvas.bind("<ButtonRelease-1>", self.__handle_button_release)

        # Mouse Scroll
        self.canvas.bind("<MouseWheel>", self.__handle_zoom)

        # Drag mode
        self.canvas.bind("<KeyPress-space>", self.__set_drag_mode)
        self.canvas.bind("<KeyRelease-space>", self.__set_drag_mode)

        # Zoom mode
        self.canvas.bind("<KeyPress-Control_L>", self.__set_zoom_mode)
        self.canvas.bind("<KeyRelease-Control_L>", self.__set_zoom_mode)

    def create_canvas_grid(self):
        """
        Create canvas grid. Used to generate the grid on the canvas.
        """
        cwidth = self.winfo_screenwidth() * 2
        cheight = self.winfo_screenheight() * 2

        # Create the grid
        for x1 in range(0, cwidth-self.grid_size, self.grid_size):
            x2 = x1 + self.grid_size
            for y1 in range(0, cheight-self.grid_size, self.grid_size):
                y2 = y1 + self.grid_size
                self.canvas.create_rectangle(x1, y1, x2, y2)

        # Set scroll region within the confines of the grid
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

