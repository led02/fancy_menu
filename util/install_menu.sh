#!/bin/bash

CARD10_ROOT=$1

if [ "x$CARD10_ROOT" = "x" ]
then
    echo "Usage: $0 CARDIO_ROOT [-app]"
    exit 1
fi


if [ "x$2" == "x-app" ]
then
    echo "Install fancy menu app..."
    cp -r ../menu $CARD10_ROOT/apps
else
    echo "Install fancy menu as default..."
    cp ../menu/__init__.py $CARD10_ROOT/menu.py
    cp ../menu/*.icx $CARD10_ROOT
fi

if [ -f menu.json ]
then
    echo "Copy menu config..."
    cp menu.json $CARD10_ROOT
fi

sync
