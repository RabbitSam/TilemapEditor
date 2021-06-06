import tkinter as tk
from typing import MutableSequence, Union, Tuple
import math
from mode import Modes
from copy import deepcopy
from queue import Queue
from threading import Thread


class InfiniteCanvas2(tk.Frame):
    def __init__(self, master=None, mode=None, **kwargs):
        """
        Initializes an infinite canvas that can be drag scrolled.

        :param master: The master holding the frame.
        :param width: The width of the frame.
        :param height: The height of the frame.
        """
        # Super class init
        super().__init__(master=master, **kwargs)

        # Canvas
        self.__canvas = None
        self.__cscrollbars: MutableSequence[Union[tk.Scrollbar, None]] = [None, None]   # Scrollbars (x, y)

        # Grid size
        self.__grid_size_old = 50
        self.__grid_size = 50
        self.__growth_rate = 1.2
        self.__grid_size_bounds = [25, 100]
        self.__csize = self.__round_to_gridsize((self.winfo_screenwidth() * 2, self.winfo_screenheight() * 2))

        # Resize boxes
        self.__resize_box_size = 10

        # Modes
        self.__mode = mode

        # Event related variables
        self.__motion_item = None
        self.__candidate_item = None
        self.__selected_item = None
        self.__resize_candidate_item = None
        self.__resize_boxes = {
            "left": {
                "iid": None,
                "opposite": "right",
                "alternate": ("top", "bottom")
            },
            "right": {
                "iid": None,
                "opposite": "left",
                "alternate": ("top", "bottom")
            },
            "top": {
                "iid": None,
                "opposite": "bottom",
                "alternate": ("left", "right")
            },
            "bottom": {
                "iid": None,
                "opposite": "top",
                "alternate": ("left", "right")
            },
        }
        # Canvas tiles
        self.__canvas_tiles = {}

        # Create Canvas
        self.__create_canvas()
        self.__create_canvas_events()

    # CANVAS #
    def __create_canvas(self):
        """
        Creates the canvas and scrollbars
        """
        # Create a canvas with double the width and double the height so that the user has more room to work with
        self.__canvas = tk.Canvas(master=self, width=self.__csize[0], height=self.__csize[1],
                                  scrollregion=(0, 0, self.__csize[0], self.__csize[1]), confine=True)
        self.__canvas.configure(bg="grey")
        self.__canvas.images = dict()

        # Scrollbars
        self.__cscrollbars[0] = tk.Scrollbar(master=self, orient=tk.HORIZONTAL, command=self.__canvas.xview)
        self.__cscrollbars[1] = tk.Scrollbar(master=self, orient=tk.VERTICAL, command=self.__canvas.yview)

        # Pack
        self.__cscrollbars[0].pack(side=tk.BOTTOM, fill=tk.X)
        self.__cscrollbars[1].pack(side=tk.RIGHT, fill=tk.Y)

        # Pack Canvas
        self.__canvas.config(xscrollcommand=self.__cscrollbars[0].set, yscrollcommand=self.__cscrollbars[1].set)
        self.__canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.__canvas.focus_set()

    def __create_canvas_events(self):
        """
        Create canvas events. Used to bind events to the canvas widget.
        """
        # Modifier keys
        # Zoom
        self.__canvas.bind("<KeyPress-Control_L>", self.set_zoom_mode, add="+")
        self.__canvas.bind("<KeyRelease-Control_L>", self.set_zoom_mode, add="+")

        # Drag
        self.__canvas.bind("<KeyPress-space>", self.set_drag_mode, add="+")
        self.__canvas.bind("<KeyRelease-space>", self.set_drag_mode, add="+")

        # Set Cursor
        self.__canvas.bind("<Enter>", self.handle_enter_exit)
        self.__canvas.bind("<Leave>", self.handle_enter_exit)

        # Click, Motion and Release Events
        self.__canvas.bind("<ButtonRelease-1>", self.handle_button_release, add="+")
        self.__canvas.bind("<Button-1>", self.handle_button_click, add="+")
        self.__canvas.bind("<B1-Motion>", self.handle_button_motion, add="+")
        self.__canvas.bind("<Motion>", self.handle_motion, add="+")

        # Mouse Wheel Events
        self.__canvas.bind("<MouseWheel>", self.handle_scroll, add="+")

    def __map_to_grid(self, coords: Tuple[int, int]) -> Tuple[int, int]:
        """
        Maps a given set of coordinates (x, y) onto grid squares mathematically
        :param coords: a tuple of coordinates (x, y)
        :return: A tuple (x, y) the coordinates on the top left corner of the mapped square on the grid
        """
        x, y = self.__round_to_gridsize(coords)
        upper_bounds = self.__csize[0] - self.__grid_size, self.__csize[1] - self.__grid_size
        return max(0, min(x, upper_bounds[0])), max(0, min(y, upper_bounds[1]))

    def __round_to_gridsize(self, coords: Tuple[int, int]) -> Tuple[int, int]:
        """
        Rounds down a pair of coordinates (x, y) to the nearest gridsize.
        :param coords: a tuple of coordinates (x, y)
        :return: A tuple (x, y) the coordinates on the top left corner of the mapped square on the grid
        """
        return (coords[0] // self.__grid_size) * self.__grid_size,\
               (coords[1] // self.__grid_size) * self.__grid_size

    # EVENTS #
    # -- Mode Events -- #
    def set_zoom_mode(self, event):
        """
        Sets the current mode to zoom
        :param event: The tkinter event
        """
        etype = str(event.type)
        if etype == "KeyPress" and self.__mode != Modes.DRAG:
            self.__mode.archive_mode()
            self.__mode.set_mode(Modes.ZOOM)
        elif etype == "KeyRelease":
            self.__mode.unarchive_mode()
        self.__canvas.config(cursor=self.__mode.get_cursor())

    def set_drag_mode(self, event):
        """
        Sets the current mode to drag
        :param event: The tkinter event
        """
        etype = str(event.type)
        if etype == "KeyPress" and self.__mode != Modes.ZOOM:
            self.__mode.archive_mode()
            self.__mode.set_mode(Modes.DRAG)
        elif etype == "KeyRelease":
            self.__mode.unarchive_mode()
        self.__canvas.config(cursor=self.__mode.get_cursor())

    # -- Canvas Events -- #
    def __resize_to_grid(self, sprite):
        """
        Resizes sprite to grid
        :param sprite: The sprite to resize
        """
        # Resize the sprite if its size doesn't match the grid size
        size = sprite.get_size()
        if size[0] != self.__grid_size or size[1] != self.__grid_size:
            sprite.resize((self.__grid_size, self.__grid_size))
            sprite.snap_to_ratio()

    def handle_button_motion(self, event):
        """
        Handles Left Mouse Button "held and drag" events
        :param event: The tkinter event
        """
        if self.__mode == Modes.DRAG:
            self.__canvas.scan_dragto(event.x, event.y, gain=1)

    def handle_button_release(self, event):
        pass

    def handle_button_click(self, event):
        """
        Handles Left Mouse Button Click events
        :param event: The tkinter event
        """
        if self.__mode == Modes.DRAG:
            self.__canvas.scan_mark(event.x, event.y)
        elif self.__mode == Modes.ADD:
            sprite = deepcopy(self.__motion_item["sprite"])

            self.__resize_to_grid(sprite)

            # Get the proper coordinates
            coords = self.__canvas.canvasx(event.x), self.__canvas.canvasy(event.y)
            coords = self.__map_to_grid(coords)

            # Draw the image
            photoimage = sprite.get_photo_image()
            iid = self.__canvas.create_image(*coords, image=photoimage, anchor=tk.NW)
            self.__canvas.images[iid] = photoimage

            self.__canvas_tiles[iid] = {
                "sprite": sprite,
                "rowcol": (coords[0] // self.__grid_size, coords[1] // self.__grid_size)
            }

            self.__create_tile_events(iid, sprite)

    def __create_tile_events(self, iid, sprite):
        """
        Creates the necessary events for tiles on the canvas
        :param iid: The iid of the tile
        :param sprite: The sprite associated with the tile
        """
        # Create tile specific events
        def move_tile(event, iid=iid, sprite=sprite):
            self.move_tile(event, iid, sprite)

        def move_tile_complete(event, iid=iid, sprite=sprite):
            self.move_tile_complete(event, iid, sprite)

        def select_tile(event, iid=iid, sprite=sprite):
            self.select_tile(event, iid, sprite)

        self.__canvas.tag_bind(iid, "<B1-Motion>", move_tile, add="+")
        self.__canvas.tag_bind(iid, "<ButtonRelease-1>", move_tile_complete, add="+")
        self.__canvas.tag_bind(iid, "<Button-1>", select_tile, add="+")

    def handle_enter_exit(self, event):
        """
        Handles mouse events on entering and exiting the canvas
        """
        etype = str(event.type)
        if etype == "Enter":
            self.__canvas.config(cursor=self.__mode.get_cursor())
        elif etype == "Leave":
            self.__canvas.config(cursor="arrow")
            self.__delete_motion_item()

    def handle_scroll(self, event):
        """
        Handles Mouse Wheel events
        :param event: The tkinter event
        """
        if self.__mode == Modes.ZOOM:
            # This is to determine the final size of the canvas
            # Currently the way is to get this value and then multiply the final grid size.
            # This is to avoid accidentally changing the number of squares that should exist in the canvas.
            # This extra calculation can be removed if this size is put at class definition.
            # Temporarily keeping this here until I make sure this is the only good way of doing this.
            row_squares = self.__csize[0] / self.__grid_size
            col_squares = self.__csize[1] / self.__grid_size

            self.__grid_size_old = self.__grid_size

            # Check whether to shrink the canvas or to grow the canvas
            if event.delta < 0:
                self.__grid_size = round(self.__grid_size * (1 / self.__growth_rate))
                if self.__grid_size < self.__grid_size_bounds[0]:
                    self.__grid_size = self.__grid_size_bounds[0]
            else:
                self.__grid_size = round(self.__grid_size * self.__growth_rate)
                if self.__grid_size > self.__grid_size_bounds[1]:
                    self.__grid_size = self.__grid_size_bounds[1]

            # If it actually resized then do all the necessary processing
            if self.__grid_size != self.__grid_size_old:
                self.__delete_resize_boxes()

                self.__csize = self.__grid_size * row_squares, self.__grid_size * col_squares

                self.__canvas.configure(width=self.__csize[0], height=self.__csize[1])
                self.__canvas.configure(scrollregion=(0, 0, self.__csize[0], self.__csize[1]))

                # Resize tiles in threads
                iids = list(self.__canvas_tiles.keys())
                length = len(iids)
                num_groups = 10
                portion = length//num_groups

                for i in range(1, num_groups + 1):
                    start = (i - 1) * portion
                    end = i * portion if i < num_groups else length
                    group = iids[start:end]

                    tt = ThreadedTask(self.__zoom_tiles, event, group)
                    tt.start()

    def __zoom_tiles(self, event, group):
        """
        Zooms a certain number of tiles (specified by group)
        :param event: The tkinter event
        :param group: The group of tile iids
        """
        for iid in group:
            self.__move_and_resize_image(event, iid)

    def handle_motion(self, event):
        """
        Handles events for when the mouse is moved in the canvas
        :param event: The tkinter event
        """
        if self.__mode == Modes.ADD:
            # In ADD mode, this is going to be used to create a ghosting effect for the item to show the user
            # where the object will be placed when they place the sprite
            # The motion item is used to keep track of the selected sprite
            if self.__motion_item is None and self.__mode.has_related_item():
                sprite = deepcopy(self.__mode.get_related_item())

                self.__resize_to_grid(sprite)

                # Calculate the coordinates for ghosting
                coords = self.__canvas.canvasx(event.x), self.__canvas.canvasy(event.y)
                coords = self.__map_to_grid(coords)

                # Draw the ghost image
                ghost = sprite.get_ghost_photoimage()
                iid = self.__canvas.create_image(*coords, image=ghost, anchor=tk.NW)
                self.__canvas.images[iid] = ghost

                self.__motion_item = {
                    "iid": iid,
                    "sprite": sprite
                }

            else:
                iid = self.__motion_item["iid"]
                sprite = self.__motion_item["sprite"]

                # Resize the sprite if the sprite's size doesn't match the grid size
                size = sprite.get_size()
                resized = False
                if size[0] != self.__grid_size or size[1] != self.__grid_size:
                    sprite.resize((self.__grid_size, self.__grid_size))
                    resized = True

                # Get the ghosting location
                coords = self.__canvas.canvasx(event.x), self.__canvas.canvasy(event.y)
                coords = self.__map_to_grid(coords)

                # If the sprite was resized then replace it with the resized sprite, if not then move it
                if resized:
                    ghost = sprite.get_ghost_photoimage()
                    self.__canvas.itemconfigure(iid, image=ghost)
                    self.__canvas.images[iid] = ghost

                else:
                    self.__canvas.coords(iid, *coords)

        else:
            self.__delete_motion_item()

    # -- Canvas Tile Events -- #
    def __resize_image(self, event, iid):
        """
        Resize image in the canvas to match that of the gridsize of the canvas
        :param event: The event
        :param iid: The id of the image
        """
        # Get sprite
        sprite = self.__canvas_tiles[iid]["sprite"]
        # Resize the sprite only if it needs resizing
        size = sprite.get_size()
        if size[0] != self.__grid_size or size[1] != self.__grid_size:
            sprite.resize((self.__grid_size, self.__grid_size))
            sprite.snap_to_ratio()

            photoimage = sprite.get_photo_image()
            self.__canvas.itemconfigure(iid, image=photoimage)
            self.__canvas.images[iid] = photoimage

    def __move_and_resize_image(self, event, iid):
        """
        Moves and Resizes an image. For zoom purposes.
        :param event: The tkinter event
        :param iid: The iid of the sprite to move and resize
        """
        rowcol = self.__canvas_tiles[iid]["rowcol"]
        new_coords = rowcol[0] * self.__grid_size, rowcol[1] * self.__grid_size
        self.__canvas.coords(iid, *new_coords)
        self.__resize_image(event, iid)

    def __delete_motion_item(self):
        """
        Deletes ghost image from the canvas.
        """
        # Delete Motion Item and Related data from canvas
        if self.__motion_item is not None:
            iid = self.__motion_item["iid"]
            self.__canvas.delete(iid)
            del self.__canvas.images[iid]
            self.__motion_item = None

    def __delete_candidate_item(self):
        """
        Deletes candidate ghost image from the canvas
        """
        # Delete Motion Item and Related data from canvas
        if self.__candidate_item is not None:
            iid = self.__candidate_item["iid"]
            self.__canvas.delete(iid)
            del self.__canvas.images[iid]
            self.__candidate_item = None

    def move_tile(self, event, iid, sprite):
        """
        Tile moving event
        :param event: The tkinter event
        :param iid: id of the item in the canvas
        :param sprite: The related sprite
        """
        if self.__mode == Modes.EDIT:
            self.__canvas.itemconfigure(iid, anchor=tk.CENTER)

            coords = self.__canvas.canvasx(event.x), self.__canvas.canvasy(event.y)
            sprite_coords = self.__canvas.coords(iid)
            difference = coords[0] - sprite_coords[0], coords[1] - sprite_coords[1]
            self.__canvas.move(iid, *difference)

            # Create or move the candidate ghost item
            candidate_coords = self.__get_candidate_coords(self.__canvas.bbox(iid), sprite.get_ratio())
            if self.__candidate_item is None:
                photo_image = sprite.get_ghost_photoimage()
                gid = self.__canvas.create_image(*candidate_coords, image=photo_image, anchor=tk.NW)
                self.__canvas.images[gid] = photo_image

                self.__candidate_item = {
                    "iid": gid,
                    "sprite": sprite
                }

            else:
                gid = self.__candidate_item["iid"]
                self.__canvas.coords(gid, candidate_coords)

            rowcol = candidate_coords[0] // self.__grid_size, candidate_coords[1] // self.__grid_size
            self.__canvas_tiles[iid]["rowcol"] = rowcol

    def move_tile_complete(self, event, iid, sprite):
        """
        Called after a tile has been moved
        :param event: The tkinter event
        :param iid: The id of the canvas
        :param sprite: The sprite object of the tile
        """
        final_coords = self.__canvas.coords(self.__candidate_item["iid"])
        self.__canvas.itemconfigure(iid, anchor=tk.NW)
        self.__canvas.coords(iid, final_coords)

        self.__delete_candidate_item()
        self.__delete_resize_boxes()
        self.__create_resize_boxes(iid, sprite)

    def __get_candidate_coords(self, bbox, ratio):
        """
        Used to calculate the final coordinates of the candidate
        :param bbox: The bounding box of the the image
        :param ratio: The size ratio of the image
        :return: The coords where the candidate should be
        """
        x_coords = bbox[0], bbox[2]
        y_coords = bbox[1], bbox[3]

        # Go through each of the corners of the bounding box to determine the most appropriate square
        # The idea is to find which corner of the is closest to the same corner of the square on the board
        final_coords = None
        final_distance = None
        for i in range(len(x_coords)):
            for j in range(len(y_coords)):
                current = list(self.__map_to_grid((x_coords[i], y_coords[j])))

                # Add grid size because this is the right/bottom corner
                if i % 2 != 0:
                    current[0] += self.__grid_size

                if j % 2 != 0:
                    current[1] += self.__grid_size

                diffs = current[0] - x_coords[i], current[1] - y_coords[j]
                current_distance = math.sqrt((diffs[0] * diffs[0]) + (diffs[1] * diffs[1]))

                if final_coords is None:
                    final_coords = current
                    final_distance = current_distance
                elif current_distance < final_distance:
                    final_coords = current
                    final_distance = current_distance

                    # Subtract grid size because the anchor is the nw corner
                    if i % 2 != 0:
                        final_coords[0] -= (self.__grid_size * ratio[0])

                    if j % 2 != 0:
                        final_coords[1] -= (self.__grid_size * ratio[1])

        return final_coords

    # -- Tile Resize Events -- #
    def select_tile(self, event, iid, sprite):
        """
        Selects a tile
        :param event: The tkinter event
        :param iid: The iid of the tile to be selected
        :param sprite: The related sprite
        """
        if self.__mode == Modes.EDIT:
            self.__selected_item = {
                "iid": iid,
                "sprite": sprite
            }

            self.__create_resize_boxes(iid, sprite)

    def __create_resize_boxes(self, iid, sprite):
        """
        Creates the resize boxes around a tile
        :param iid: The id of the tile
        :param sprite: The sprite object
        """
        # Delete resize boxes
        self.__delete_resize_boxes()

        # Set the for corner coordinates
        bbox = self.__canvas.bbox(iid)
        size = sprite.get_size()
        half_rb_size = self.__resize_box_size // 2
        coords = {
            "left": (bbox[0] - self.__resize_box_size, bbox[1] + (size[1] // 2) - half_rb_size),
            "top": (bbox[0] + (size[0] // 2) - half_rb_size, bbox[1] - self.__resize_box_size),
            "right": (bbox[2], bbox[1] + (size[1] // 2) - half_rb_size),
            "bottom": (bbox[0] + (size[0] // 2) - half_rb_size, bbox[3])
        }

        for key in coords:
            # x0, y0, x1, y1
            final = coords[key][0], coords[key][1],\
                    coords[key][0] + self.__resize_box_size, coords[key][1] + self.__resize_box_size
            rid = self.__canvas.create_rectangle(*final, fill="white")

            self.__resize_boxes[key]["iid"] = rid

            # Resize events
            def drag_resize_tile(event, side=key):
                self.drag_resize_tile(event, side)

            def drag_resize_complete(event):
                self.drag_resize_complete(event)

            self.__canvas.tag_bind(rid, "<B1-Motion>", drag_resize_tile, add="+")
            self.__canvas.tag_bind(rid, "<ButtonRelease-1>", drag_resize_complete, add="+")

    def __delete_resize_boxes(self):
        """
        Destroys resize boxes
        """
        for key in self.__resize_boxes:
            # Only need to delete if they actually exist
            if self.__resize_boxes[key]["iid"] is not None:
                self.__canvas.delete(self.__resize_boxes[key]["iid"])
                self.__resize_boxes[key]["iid"] = None

    def drag_resize_tile(self, event, side):
        """
        Drag resize a tile
        :param event: The tkinter event
        :param side: The side
        """
        tid = self.__selected_item["iid"]
        sprite = self.__selected_item["sprite"]

        if side in ("top", "bottom"):
            rid = self.__resize_boxes[side]["iid"]

            new_y = self.__canvas.canvasy(event.y)
            old_coords = self.__canvas.coords(rid)
            y_diff = round(new_y - old_coords[1])

            self.__canvas.move(rid, 0, y_diff)

            size = list(sprite.get_size())

            if side == "top":
                size[1] += (y_diff * -1)
                self.__canvas.move(tid, 0, y_diff)

            else:
                size[1] += y_diff

        else:
            rid = self.__resize_boxes[side]["iid"]

            new_x = self.__canvas.canvasx(event.x)
            old_coords = self.__canvas.coords(rid)
            x_diff = round(new_x - old_coords[0])

            self.__canvas.move(rid, x_diff, 0)

            size = list(sprite.get_size())

            if side == "left":
                size[0] += (x_diff * -1)
                self.__canvas.move(tid, x_diff, 0)

            else:
                size[0] += x_diff

        # Resize the sprite
        sprite.resize(tuple(size))
        photoimage = sprite.get_photo_image()
        self.__canvas.itemconfigure(tid, image=photoimage)
        self.__canvas.images[tid] = photoimage

        # Create or resize the candidate item
        bbox = self.__canvas.bbox(tid)
        nw = self.__map_to_grid((bbox[0] + (self.__grid_size // 2), bbox[1] + (self.__grid_size // 2)))
        se = self.__map_to_grid((bbox[2] + (self.__grid_size // 2), bbox[3] + (self.__grid_size // 2)))

        size = se[0] - nw[0], se[1] - nw[1]
        ratio = size[0] // self.__grid_size, size[1] // self.__grid_size
        if self.__resize_candidate_item is None:
            # Copy sprite
            copy_sprite = deepcopy(sprite)
            copy_sprite.resize((self.__grid_size, self.__grid_size))
            copy_sprite.set_ratio(ratio)
            copy_sprite.snap_to_ratio()

            # Create ghost image
            photo_image = copy_sprite.get_ghost_photoimage()
            rcid = self.__canvas.create_image(*nw, image=photo_image, anchor=tk.NW)
            self.__canvas.images[rcid] = photo_image

            self.__resize_candidate_item = {
                "iid": rcid,
                "sprite": copy_sprite
            }

        else:
            rcid = self.__resize_candidate_item["iid"]
            rcsprite = self.__resize_candidate_item["sprite"]

            rcsprite.set_ratio(ratio)
            rcsprite.resize((self.__grid_size, self.__grid_size))
            rcsprite.snap_to_ratio()

            # Create ghost image
            photo_image = rcsprite.get_ghost_photoimage()
            self.__canvas.itemconfigure(rcid, image=photo_image)
            self.__canvas.coords(rcid, *nw)
            self.__canvas.images[rcid] = photo_image

        rowcol = self.__canvas.coords(rcid)[0] // self.__grid_size, self.__canvas.coords(rcid)[1] // self.__grid_size
        self.__canvas_tiles[rcid]["rowcol"] = rowcol

    def drag_resize_complete(self, event):
        """
        Called after the drag resizing is done
        :param event: The tkinter event
        """
        tid = self.__selected_item["iid"]
        sprite = self.__selected_item["sprite"]

        # Get data from candidate sprite
        csprite_ratio = self.__resize_candidate_item["sprite"].get_ratio()
        clocation = self.__canvas.coords(self.__resize_candidate_item["iid"])

        # Apply data from candidate sprite to new sprite
        self.__canvas.coords(tid, clocation)
        sprite.set_ratio(csprite_ratio)
        sprite.resize((self.__grid_size, self.__grid_size))
        sprite.snap_to_ratio()

        photo_image = sprite.get_photo_image()
        self.__canvas.itemconfigure(tid, image=photo_image)
        self.__canvas.images[tid] = photo_image

        self.__delete_resize_candidate_item()

        # Temporary, might change to just moving the alternate boxes later
        self.__delete_resize_boxes()
        self.__create_resize_boxes(tid, sprite)

    def __delete_resize_candidate_item(self):
        """
        Deletes resize candidate image from the canvas.
        """
        # Delete Resize candidate Item and Related data from canvas
        if self.__resize_candidate_item is not None:
            iid = self.__resize_candidate_item["iid"]
            self.__canvas.delete(iid)
            del self.__canvas.images[iid]
            self.__resize_candidate_item = None


class ThreadedTask(Thread):
    def __init__(self, action, *args):
        super().__init__()
        self.action = action
        self.args = args

    def run(self):
        self.action(*self.args)
