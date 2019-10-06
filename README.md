Fancy menu for your card10 badge
================================

This app implements a fancy menu with icon support for your card10 badge.


Usage as app
------------

Simply copy the `menu` folder to your card10 `/apps` directory.


Usage as default menu
---------------------

- Replace `menu.py` on your card10 with `menu/__init__.py`.
- Copy all `*.icx` files from the `menu` folder to your card10 root. Instead of
  manually copying the files, you can also run `install_icons.sh` (see below).


Add icons to your apps
----------------------

Icons are stored in plain binary format. They are assumed to have a size of 48x48
pixels. Those are stored row by row as byte tuples containing red, green, blue,
and alpha channel.

You can use the script in `utils/img2icx.py` that converts images to the right
file format. To add the icon to an app, simply name it `icon.icx` and put it inside the app
module alongside your `metadata.json`.

Some of the camp icons are in the icons directory **(also required default icons)**.
You can prepare and install them using the `install_icons.sh` script:

    $ cd icons
    $ ./install_icons.sh $CARD10_ROOT

where `$CARD10_ROOT` is the path where your card10 is mounted.


Technical dept
--------------

- Animation is pretty slow, a blit function built into the display might be nice.
- Image loading is slow - due to alpha corrections? However, there is only enough
  memory for max three icons 48x48. Sometimes, if the GC is to slow, even an image
  might be dropped. (Handled graceful.)
- Enable configuration of foreground / background color.
- Enable tapping interface using BMA400 sensor.
