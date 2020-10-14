import tkinter as tk
from Canvas.InfiniteCanvas import InfiniteCanvas


def main():
    """
    Main function. Creates the window and the canvas.
    """
    window = tk.Tk()
    canvas = InfiniteCanvas(master=window)
    canvas.pack()

    window.geometry("500x500")
    window.mainloop()


if __name__ == "__main__":
    main()
