import tkinter as tk
import math


class InfiniteCanvas(tk.Frame):
    def __init__(self, master=None, width: int = 50, height: int = 50):
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
        self.xscrollbar = None
        self.yscrollbar = None

        # Frame data
        self.width = width
        self.height = height

        # Instance data
        # Modes
        self.mode = ""

        # Dragging variables
        self.drag_src_coords = (-1, -1)  # (x, y)

        # Create canvas and children
        self.create_canvas()

    # ------------------------------------ Events --------------------------------------- #
    def __handle_button_motion(self, event):
        """
        Handle button motion events.
        Use this for mouse drag events (eg. Drag scrolling, drag moving items in the canvas, ..)

        :param event: The tkinter event.
        """
        # If the current mode is drag
        if self.mode == "drag":
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
        if self.mode == "drag":
            self.drag_src_coords = (-1, -1)

    def __set_drag_mode(self, event):
        """
        Set Drag Mode. Used to enable and disable drag events.

        :param event: The tkinter event
        """
        # Check whether to activate or deactivate the drag event
        if str(event.type) == "KeyPress" and self.mode != "drag":
            self.mode = "drag"
            self.canvas.config(cursor="fleur")
        elif str(event.type) == "KeyRelease":
            # Reset Drag variables
            self.mode = ""
            self.drag_src_coords = (-1, -1)
            self.canvas.config(cursor="arrow")

    # ----------------------------------- Canvas Method ------------------------------------ #
    def create_canvas(self):
        """
        Create and pack the canvas.
        """
        # Create a canvas with double the width and double the height so that the user has more room to work with
        cwidth = self.winfo_screenwidth()*2
        cheight = self.winfo_screenheight()*2
        self.canvas = tk.Canvas(master=self, width=cwidth, height=cheight, scrollregion=(0, 0, cwidth, cheight))
        self.canvas.configure(bg="grey")    # To see if it is being rendered correctly

        # XScrollbar
        self.xscrollbar = tk.Scrollbar(master=self, orient=tk.HORIZONTAL)
        self.xscrollbar.config(command=self.canvas.xview)

        # YScrollbar
        self.yscrollbar = tk.Scrollbar(master=self, orient=tk.VERTICAL)
        self.yscrollbar.config(command=self.canvas.yview)

        # Pack
        self.xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack Canvas
        self.canvas.config(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.canvas.focus_set()

        # Create events for the canvas
        self.canvas.bind("<B1-Motion>", self.__handle_button_motion)
        self.canvas.bind("<ButtonRelease-1>", self.__handle_button_release)

        self.canvas.bind("<KeyPress-space>", self.__set_drag_mode)
        self.canvas.bind("<KeyRelease-space>", self.__set_drag_mode)





