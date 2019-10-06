Fancy menu for your card10 badge
================================

This app implements a fancy menu with icon support for your card10 badge.


Installation
------------

Use the `util/install_menu.sh` to install the menu on your card10. You should
pass the path to the root directory of your mounted watch. If you want to install
it as application, append `-app` to the call:

    $ cd util
    
    # Install as default menu:
    $ ./install_menu.sh $CARD10_ROOT
    
    # Install as app:
    $ ./install_menu.sh $CARD10_ROOT -app


Configuration
-------------

You can put a `menu.json` in your root folder. Here you can define values for
background color (`bg`) and text color (`fg`). Both should be hexadecimal values
without leading `0x` in RGB order.


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
- Enable tapping interface using BMA400 sensor.
