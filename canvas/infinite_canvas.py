import tkinter as tk
import math
from mode import Modes
from copy import deepcopy
from time import sleep


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
        self._grid_size = [50, 50]

        # Canvas width and height
        self._cwidth = self.winfo_screenwidth() * 2
        self._cheight = self.winfo_screenheight() * 2

        # Frame data
        self._width = width
        self._height = height

        # Instance data
        # Modes
        self._mode = mode

        # Grids
        self._canvas_grid = []
        self._resize_box_size = 5

        # Tiles
        self._tiles = dict()
        self._selected_tile = ""
        self._resize_boxes = dict()
        self._borderwidth = 1

        # Moving
        self._moving = False

        # Visible items
        # self.__visible_items = []

        # Create canvas
        self._create_canvas()
        self._create_canvas_events()
        self._create_canvas_grid()

    # ------------------------------------ Canvas Events --------------------------------------- #
    def _handle_button_motion(self, event, related_item_id=None):
        """
        Handle button motion events.
        Use this for mouse drag events (eg. Drag scrolling, drag moving items in the canvas, ..)

        :param event: The tkinter event.
        :param related_item_id: The id of the item on the canvas if needed
        """
        # If the current mode is drag
        if self._mode == Modes.DRAG:
            self._canvas.scan_dragto(event.x, event.y, gain=1)
            self._generate_zoom_event()
        elif self._mode == Modes.EDIT and related_item_id is not None:
            # If just started moving the move the anchor and get rid of the resize boxes
            if not self._moving:
                # TODO: Add 'Held' Cursor
                self._destroy_resize_boxes()
                self._canvas.itemconfigure(related_item_id, anchor=tk.CENTER)
                self._moving = True

            # Otherwise move the item
            else:
                item_coords = self._canvas.coords(related_item_id)

                # Calculate mouse coords
                current_x = max(self._canvas.canvasx(event.x), 0)
                current_y = max(self._canvas.canvasy(event.y), 0)

                # Move the item
                self._canvas.move(related_item_id, current_x - item_coords[0], current_y - item_coords[1])

    def _handle_button_release(self, event, related_item_id=None):
        """
        Handle button release events.
        Use primarily to reset some button motion changes.

        :param event: The tkinter event.
        """
        if self._mode == Modes.EDIT and related_item_id is not None:
            # Set changed values to default
            self._moving = False
            corners = self._canvas.bbox(related_item_id)
            self._canvas.itemconfigure(related_item_id, anchor="nw")

            # Calculate the pointer location in the widget
            current_x = max(self._canvas.canvasx(event.x), 0)
            current_y = max(self._canvas.canvasy(event.y), 0)

            # Move this out of the way to do some processing
            item = self._tiles[related_item_id]
            ratio = item.get_ratio()
            self._canvas.coords(related_item_id, current_x + self._grid_size[0] * ratio[0],
                                current_y + self._grid_size[1] * ratio[1])

            # Snap to grid
            if ratio == (1, 1):
                rect_id = self._canvas.find_closest(current_x, current_y)
                bbox_rect = self._canvas.bbox(rect_id)
            else:
                # Get all the candidate squares to find the "Most Correct" location
                candidates = list()
                # item_id, corner, offset_multiplier, borderwidth_offset
                candidates.append((self._canvas.find_closest(corners[0], corners[1]), (0, 1), (0, 0)))  # nw
                candidates.append((self._canvas.find_closest(corners[0], corners[3]), (0, 3), (0, -1)))  # sw
                candidates.append((self._canvas.find_closest(corners[2], corners[1]), (2, 1), (-1, 0)))  # ne
                candidates.append((self._canvas.find_closest(corners[2], corners[3]), (2, 3), (-1, -1)))  # se

                # Get the squared distances, no need for square root since I only to compare
                min_distance = -1
                final_candidate = None
                for i, candidate in enumerate(candidates):
                    indxs = candidate[1]
                    coords = self._canvas.bbox(candidate[0])

                    distance_squared = (coords[indxs[0]] - current_x)**2 + (coords[indxs[1]] - current_y)**2
                    if min_distance == -1 or distance_squared < min_distance:
                        min_distance = distance_squared
                        final_candidate = candidate

                # Using a list to make it mutable
                candidate_bbox = list(self._canvas.bbox(final_candidate[0]))
                final_x = candidate_bbox[final_candidate[1][0]] \
                          + (ratio[0] * self._grid_size[0] * final_candidate[2][0] + (self._grid_size[0] // 2))
                final_y = candidate_bbox[final_candidate[1][1]] \
                          + (ratio[1] * self._grid_size[1] * final_candidate[2][1] + (self._grid_size[1] // 2))

                # Final location
                rect_id = self._canvas.find_closest(final_x, final_y)
                bbox_rect = self._canvas.bbox(rect_id)

            # Move the tile
            self._canvas.coords(related_item_id, bbox_rect[0] + self._borderwidth, bbox_rect[1] + self._borderwidth)

            # Draw resize boxes
            self._create_resize_boxes(related_item_id)

    def _handle_zoom(self, event):
        """
        Handles zoom related events.

        :param event: The tkinter event.
        """
        if self._mode == Modes.ZOOM:
            scale_factor = 1.001 ** event.delta     # The amount to scale by

            # Scale the page
            self._canvas.scale(tk.ALL, event.x, event.y, scale_factor, scale_factor)

            # Set the scroll region to within the bbox
            self._canvas.config(scrollregion=self._canvas.bbox(tk.ALL))

            # Recalculate grid size
            bbox = self._canvas.bbox("ref_rect")
            self._grid_size[0] = bbox[2] - bbox[0]
            self._grid_size[1] = bbox[3] - bbox[1]

            # Generate zoom event
            self._generate_zoom_event()

            # Redraw Resize boxes
            if self._selected_tile != "":
                self._destroy_resize_boxes()
                self._create_resize_boxes(self._selected_tile)

    def _generate_zoom_event(self):
        """
        Generates the zoom event
        :return:
        """
        # Set visible items
        # self._set_visible_items()

        # Resize photo images
        self._canvas.event_generate("<<zoom>>")

    def _handle_canvas_click(self, event):
        """
        Clicked event callback

        :param event: The tkinter event
        """
        if self._mode == Modes.DRAG:
            self._canvas.scan_mark(event.x, event.y)
        elif self._mode == Modes.ADD and self._mode.has_related_item():
            # Calculate coords
            bbox = self._canvas.bbox(tk.CURRENT)
            coords = bbox[0] + self._borderwidth, bbox[1] + self._borderwidth

            # Copy and resize the image
            image = deepcopy(self._mode.get_related_item())
            image.resize(self._grid_size)
            photo_image = image.get_photo_image()

            # Add the image to the canvs
            image_id = self._canvas.create_image(coords[0], coords[1], image=photo_image, anchor="nw")
            self._canvas.images[image_id] = photo_image
            self._tiles[image_id] = image

            # image Events
            self._canvas.bind("<<zoom>>", lambda _: self._zoom_image(image_id), add="+")
            self._canvas.tag_bind(image_id, "<Button-1>", lambda _: self._handle_image_click(image_id), add="+")
            self._canvas.tag_bind(image_id, "<B1-Motion>", lambda e: self._handle_button_motion(e, image_id), add="+")
            self._canvas.tag_bind(image_id, "<ButtonRelease-1>", lambda e: self._handle_button_release(e, image_id), add="+")

    # ------------------------------------- Tile Events ---------------------------------- #
    def _zoom_image(self, image_id):
        """
        Resizes the image
        """
        if image_id in self.__visible_items:
            self._snap_to_ratio(image_id, self._tiles[image_id].get_ratio())
            self._handle_resize_complete(image_id)

    def _snap_to_ratio(self, image_id, ratio):
        image = self._tiles[image_id]

        image.set_ratio(ratio)
        image.snap_to_ratio(list(tuple(self._grid_size)))
        self._replace_photo_image(image_id, image)

    def _replace_photo_image(self, image_id, image):
        photo_image = image.get_photo_image()
        self._canvas.itemconfigure(image_id, image=photo_image)
        self._canvas.images[image_id] = photo_image

    # def _set_visible_items(self):
    #     x1, y1 = self._canvas.canvasx(0), self._canvas.canvasy(0)
    #     x2, y2 = x1 + self._canvas.winfo_width(), y1 + self._canvas.winfo_height()
    #     print(x1, x2, y1, y2)
    #
    #     self.__visible_items = self._canvas.find_overlapping(x1, y1, x2, y2)

    def _handle_image_click(self, image_id):
        """
        Handler for when a tile is clicked

        :param image_id: Tbe id of the clicked image
        """
        if self._mode == Modes.EDIT:
            # Destroy old resize boxes
            self._destroy_resize_boxes()

            # Select the tile
            self._selected_tile = image_id

            # Create resize boxes
            self._create_resize_boxes(image_id)

    # ------------------------------------- Resize Events -------------------------------- #
    def _handle_resize_box(self, event, side, image_id):
        """
        Handle resizing using the resize box

        :param side: The side with the box
        :param image_id: The id of the image
        """
        # Get Image
        image = self._tiles[image_id]

        # Set ratio
        image.reset_ratio()

        # Get the boxes relevant for resizing
        selected_box_id = self._resize_boxes[side]["box_id"]
        ref_box_id = self._resize_boxes[self._resize_boxes[side]["opposite"]]["box_id"]

        # Perpendicular box id
        p_sides = self._resize_boxes[side]["perpendicular"]
        p_box_ids = self._resize_boxes[p_sides[0]], self._resize_boxes[p_sides[1]]

        # Get the bounding boxes of the two boxes
        bbox_selected = list(self._canvas.coords(selected_box_id))
        bbox_ref = list(self._canvas.coords(ref_box_id))

        # Preset differences
        width_diff = 0
        height_diff = 0

        # Preset New values
        width = 0
        height = 0

        current_x = self._canvas.canvasx(event.x)
        current_y = self._canvas.canvasy(event.y)

        if side in ("top", "bottom"):
            # Resized coordinates
            bbox_selected[1] = current_y
            bbox_selected[3] = current_y + self._resize_box_size * 2

            # Set new height and width
            height = abs(abs(bbox_selected[1] - bbox_ref[1]) - (self._resize_box_size * 2))

            # Get height difference
            old_height = image.get_size()[1]
            height_diff = height - old_height

        else:
            # Resized coordinates
            bbox_selected[0] = current_x
            bbox_selected[2] = current_x + self._resize_box_size * 2

            # Set new height and width
            width = abs(abs(bbox_selected[0] - bbox_ref[0]) - (self._resize_box_size * 2))

            # Get width difference
            old_width = image.get_size()[0]
            width_diff = width - old_width

        # Move the selected box
        self._canvas.coords(selected_box_id, *bbox_selected)

        # Move if necessary
        if side in ("left", "top"):
            coordinates = self._canvas.coords(image_id)
            self._canvas.coords(image_id, coordinates[0] - round(width_diff), coordinates[1] - round(height_diff))

            width -= (self._resize_box_size * 2)
            height -= (self._resize_box_size * 2)

        # Resize
        image.resize((round(width), round(height)))
        self._replace_photo_image(image_id, image)

    def _handle_resize_complete(self, image_id):
        """
        Called when the resizing is completed

        :param image_id: The id of the image
        :return:
        """
        # Get the image boundaries
        width, height = self._tiles[image_id].get_size()

        # Calculate the ratio
        width_ratio = max(round(width / self._grid_size[0]), 1)
        height_ratio = max(round(height / self._grid_size[1]), 1)

        # Snap the image to the ratio
        self._snap_to_ratio(image_id, (width_ratio, height_ratio))

        # Snap the image to the rectangle on the grid
        anchor = self._canvas.coords(image_id)
        self._canvas.coords(image_id, anchor[0] + self._grid_size[0], anchor[1] + self._grid_size[1])

        rect_id = self._canvas.find_closest(*anchor)
        bbox_rect = self._canvas.bbox(rect_id)
        self._canvas.coords(image_id, bbox_rect[0] + self._borderwidth, bbox_rect[1] + self._borderwidth)

        # Resize to the actual size, not sure why multiplying and then subtracting for excluded borders doesn't work.
        # Why? Just why? Why is the size not  x1 - x2 - (borderwidth * ratio).
        # This is not efficient at all. Too bad!
        # This is a very hacky solution, very hacky. I don't like this at all.
        self._resize_to_true(image_id)

    def _resize_to_true(self, image_id):
        """
        Resizes the images to the true size.
        :param image_id:
        :return:
        """
        # Get enclosed area
        bbox_image = self._canvas.bbox(image_id)
        width = bbox_image[2] - bbox_image[0]
        height = bbox_image[3] - bbox_image[1]
        enclosed = self._canvas.find_enclosed(bbox_image[0] - self._borderwidth, bbox_image[1] - self._borderwidth,
                                              bbox_image[0] + width + self._borderwidth,
                                              bbox_image[1] + height + self._borderwidth)

        # Set candidate area
        for item in enclosed:
            tags = self._canvas.gettags(item)
            if "grid" in tags:
                self._canvas.addtag_withtag("enclosed", item)

        # Compute the final area
        final_bbox = self._canvas.bbox("enclosed")
        if final_bbox is not None:
            width = abs(final_bbox[2] - final_bbox[0])
            height = abs(final_bbox[1] - final_bbox[3])

            self._tiles[image_id].resize((width, height))
            self._replace_photo_image(image_id, self._tiles[image_id])

        # Remove the enclosure labels
        self._canvas.dtag("enclosed")

        # Redraw the resize boxes
        if self._selected_tile != "" and self._selected_tile == image_id:
            self._destroy_resize_boxes()
            self._create_resize_boxes(image_id)

    def _create_resize_boxes(self, image_id):
        """
        Create resize boxes for the given image.

        :param image_id: The id of the image
        """
        # Calculate the coordinates from the bbox
        bbox = self._canvas.bbox(image_id)
        width = abs(bbox[0] - bbox[2])
        height = abs(bbox[1] - bbox[3])
        box_coordinates = [
            ("top", (bbox[0] + (width / 2), bbox[1]), ("left", "right")),
            ("left", (bbox[0], bbox[1] + (height / 2)), ("top", "bottom")),
            ("bottom", (bbox[0] + (width / 2), bbox[1] + height), ("left", "right")),
            ("right", (bbox[0] + width, bbox[1] + (height / 2)), ("top", "bottom"))
        ]

        # Create the resize boxes
        for i, coordinates in enumerate(box_coordinates):
            if coordinates[0] in ("top", "bottom"):
                x_mul = 1
                y_mul = 2
            else:
                x_mul = 2
                y_mul = 1

            # Calculate bbox dimensions
            new_bbox = (
                coordinates[1][0] - (self._resize_box_size * x_mul), coordinates[1][1] - self._resize_box_size * y_mul,
                coordinates[1][0] + (self._resize_box_size * x_mul), coordinates[1][1] + self._resize_box_size * y_mul
            )

            # Create the resizing box
            resize_box_id = self._canvas.create_rectangle(new_bbox, fill="white")
            self._resize_boxes[coordinates[0]] = {
                "perpendicular": (coordinates[2]),
                "opposite": box_coordinates[(i + 2) % len(box_coordinates)][0],
                "box_id": resize_box_id
            }

            # This works, using a lambda function doesn't for some reason
            # I guess it's because the function is redefined each time?
            def motion_event(event, self=self, side=coordinates[0], image_id=image_id):
                self._handle_resize_box(event, side, image_id)

            def release_event(event, self=self, image_id=image_id):
                self._handle_resize_complete(image_id)

            # Add resize box tag
            self._canvas.addtag_withtag("resize_box", resize_box_id)

            # Bind the item event
            self._canvas.tag_bind(resize_box_id, "<B1-Motion>", motion_event, "+")
            self._canvas.tag_bind(resize_box_id, "<ButtonRelease-1>", release_event, "+")

    def _destroy_resize_boxes(self):
        """
        Destroy the resize boxes
        """
        self._canvas.delete("resize_box")
        self._resize_boxes = dict()

    # ------------------------- Mode Events ----------------------------- #
    def _set_drag_mode(self, event):
        """
        Set Drag Mode. Used to enable and disable drag events.

        :param event: The tkinter event
        """
        # Check whether to activate or deactivate the drag event
        if str(event.type) == "KeyPress" and self._mode != Modes.ZOOM:
            self._mode.archive_mode()
            self._mode.set_mode(Modes.DRAG)
            self._canvas.config(cursor=self._mode.get_cursor())
        elif str(event.type) == "KeyRelease":
            # Reset Drag variables
            self._mode.unarchive_mode()
            self._canvas.config(cursor=self._mode.get_cursor())

    def _set_zoom_mode(self, event):
        """
        Set Drag Mode. Used to enable and disable drag events.

        :param event: The tkinter event
        """
        # Check whether to activate or deactivate the zoom event
        if str(event.type) == "KeyPress" and self._mode != Modes.DRAG:
            self._mode.archive_mode()
            self._mode.set_mode(Modes.ZOOM)
            self._canvas.config(cursor=self._mode.get_cursor())
        elif str(event.type) == "KeyRelease":
            # Reset Zoom variables
            self._mode.unarchive_mode()
            self._canvas.config(cursor=self._mode.get_cursor())

    def _set_current_cursor(self, event):
        """
        Set the current mode

        :param event: The tkinter event
        """
        if str(event.type) == "Enter":
            self._canvas.config(cursor=self._mode.get_cursor())
        elif str(event.type) == "Leave":
            self._canvas.config(cursor="arrow")

    # ----------------------------------- Canvas Method ------------------------------------ #
    def _create_canvas(self):
        """
        Create and pack the canvas.
        """
        # Create a  canvas with double the width and double the height so that the user has more room to work with
        self._canvas = tk.Canvas(master=self, width=self._cwidth, height=self._cheight,
                                 scrollregion=(0, 0, self._cwidth, self._cheight), confine=True)
        self._canvas.configure(bg="grey")    # To see if it is being rendered correctly
        self._canvas.images = dict()

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
        self._canvas.bind("<B1-Motion>", self._handle_button_motion, add="+")
        self._canvas.bind("<ButtonRelease-1>", self._handle_button_release, add="+")

        # Mouse Scroll
        self._canvas.bind("<MouseWheel>", self._handle_zoom)

        # Drag mode
        self._canvas.bind("<KeyPress-space>", self._set_drag_mode)
        self._canvas.bind("<KeyRelease-space>", self._set_drag_mode)

        # Zoom mode
        self._canvas.bind("<KeyPress-Control_L>", self._set_zoom_mode)
        self._canvas.bind("<KeyRelease-Control_L>", self._set_zoom_mode)

        # Add mode
        self._canvas.bind("<Enter>", self._set_current_cursor)
        self._canvas.bind("<Leave>", self._set_current_cursor)

        # Mouse Click Events
        self._canvas.bind("<Button-1>", self._handle_canvas_click, add="+")

    def _create_canvas_grid(self):
        """
        Create canvas grid. Used to generate the grid on the canvas.
        """
        # Create the grid
        for x1 in range(0, self._cwidth - self._grid_size[0], self._grid_size[0]):
            x2 = x1 + self._grid_size[0]
            for y1 in range(0, self._cheight - self._grid_size[1], self._grid_size[1]):
                y2 = y1 + self._grid_size[1]
                rect_id = self._canvas.create_rectangle(x1, y1, x2, y2, fill="grey", tags=("grid"))
                if (x1, y1) == (0, 0):
                    self._canvas.addtag_withtag("ref_rect", rect_id)

        # Set scroll region within the confines of the grid
        self._canvas.config(scrollregion=self._canvas.bbox(tk.ALL))



