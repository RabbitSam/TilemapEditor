import tkinter as tk
from mode import Mode
from canvas import infinite_canvas as ic
from menu import tile_menu as tm
from menu.main_menu import MainMenu


def main():
    """
    Main function. Creates the window and the canvas.
    """
    window = tk.Tk()

    #####################################################################
    # PACKAGE THIS SECTION INTO A NEW FUNCTION OR CLASS                 #
    #####################################################################
    left_frame = tk.Frame(master=window)

    mode = Mode()
    canvas = ic.InfiniteCanvas(master=window, mode=mode)
    tile_menu = tm.TileMenu(master=left_frame, mode=mode)
    menu = MainMenu(master=left_frame, mode=mode, tile_menu=tile_menu)

    left_frame.pack(side=tk.LEFT, fill=tk.Y)
    menu.pack()
    tile_menu.pack(fill=tk.Y)
    canvas.pack(side=tk.RIGHT)
    #####################################################################

    window.geometry("500x500")
    window.mainloop()


if __name__ == "__main__":
    main()
