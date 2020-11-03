# TilemapEditor
A basic tilemap created in python using tkinter.

## Current Version
### 0.3.1
- Fixed Image positions in the grid
    - Just that, and code refactorings.

## Past Versions
### 0.3.0
- Created Add Method for Tiles
    - Uses Labels embedded into the canvas
    - This was the best way
    - In the future might look into using just the images
    - But I'll need to manually create a method to ensure that the image is visible.
    - Performance is okay. Quite a lot of visual glitches when zooming or moving though.
    - Putting that under QoL. Not sure how to fix it atm.
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

