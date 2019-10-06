#!/bin/bash

CARD10_ROOT=$1

if [ "x$CARD10_ROOT" == "x" ]
then
    echo "Usage: $0 CARD10_ROOT"
    exit 1
fi

for svg in *.svg
do
    png=$(basename -s .svg $svg).png
    echo "Convert $svg to $png"
    convert -density 300 -resize 48x48 $svg $png
    python ../util/img2icx.py $png
done

echo "Installing default icons..."
cp app.png.icx $CARD10_ROOT/app.icx
cp py.png.icx $CARD10_ROOT/py.icx
cp l0adable.png.icx $CARD10_ROOT/l0adable.icx
cp home.png.icx $CARD10_ROOT/home.icx

for icx in *.icx
do
    app=$(basename -s .png.icx $icx)
    if [ -d $CARD10_ROOT/apps/$app ]
    then
        echo "Installing icon for $app..."
        cp $icx $CARD10_ROOT/apps/$app/icon.icx
    fi
done

sync
