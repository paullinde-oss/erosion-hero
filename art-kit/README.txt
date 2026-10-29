Erosion Hero - Aseprite starter kit (see the Erosion Hero Art Spec doc)

erosion-hero.gpl      Palette. Aseprite: Palette panel options menu > Load Palette.
                      Slot 0 (magenta) is the transparent color - never paint with it.
palette-swatch.png    The same palette as a labeled picture.

tiles/*_template.png  Open in Aseprite (File > Open), set Color Mode to Indexed with the
                      palette, and keep it as a hidden 'guide' layer. Draw each tile in its
                      tinted slot. Hide the guide layer before exporting.
tiles/*_slot-map.png  Zoomed map naming every slot.

characters/*_guide.png      One tinted cell per frame, in tag order. The red bottom row is
                            where the feet go; the red vertical line is the center.
characters/*_frame-map.png  Zoomed map showing which frames belong to which tag.
                            In Aseprite, start a new file at the frame size and import the
                            guide with File > Import Sprite Sheet (Type: By Rows, size = frame size).
