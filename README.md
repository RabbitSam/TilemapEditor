# TilemapEditor
A basic tilemap created in python using tkinter.

## Current Version
### 0.7.0
- Redid how the canvas functions
    - The grid is now mathematical and no longer shows any rectangles.
        - Adding that visual element to future versions.
    - Ghosting of an image is used during adding and editing that shows how the image will look after
    an action is performed.
- Performance Optimizations for dragging and zooming
    - Dragging is not as performance heavy anymore.
    - Zooming is done with some threading which means
        - The canvas doesn't freeze when there are a large number of tiles and zooming is done.
        - Instead, the tiles resize just a little slower, I think this is an okay compromise.

## Known Bugs
### Major
- No known major bugs as of yet.

### Minor
- A tile might move away when it is resized below the size of a single grid square from the left/top
- Ghosting happens on top of the current image, thus making it look a little blurry.
- Resize boxes don't move when zooming

## Past Versions
### 0.6.1
- Added Tile Editing Options.
    - Changed from using Labels to using the canvas
    - I prefered the label way of doing things, but I feel like it was a little pointless
    - This change resulted from me being frustrated with a particular bug I kept, but considering how everything has 
    been implemented, I'm starting to wonder if this was necessary at all.
    - The current version is kind of missing the sort of kind of optimizations for images when zooming.
    - But overall I've also been thinking about the number of rectangles generated. I'm not gonna switch from my current
     way just yet. I don't think it matters, though I'm starting to wonder if I can maintain the grid by switching to a
     lines and mathematically calculating the location of the item. It will be better on performance.
     But a lot of my current features depend on rectangles, so maybe if I decide to start anew in the future at some
     point, I'll consider that.

### 0.3.1
- Fixed Image positions in the grid
    - Just that, and code refactorings.

### 0.3.0
- Created Add Method for Tiles
    - Uses Labels embedded into the canvas
    - This was the best way
    - In the future might look into using just the images
    - But I'll need to manually create a method to ensure that the image is visible.
    - Performance is okay. Quite a lot of visual glitches when zooming or moving though.
    - Putting that under QoL. Not sure how to fix it at the moment.
    - The added images are just a tiny bit outside the grid, also putting that under QoL.
 
### 0.2.0
- Created Sprite Importer
    - Uses a file dialog to load the files in.
        - Currently no restriction on file types.
    - Has a Tile Menu to render the tiles in. 
    
### 0.1.0
- The Canvas now has a grid and zooming functionality
    - The zooming is down by holding Ctrl+MouseWheel
    - Might be hard on performance, will need to keep this in check

### 0.0.0
- Created the "Infinite" Canvas
    - The canvas can be scrolled using a scroll bar
    - It can also be scrolled by holding down space, and clicking and dragging the left-mouse button.

