import struct
import sys

from PIL import Image


def main():
    if len(sys.argv) < 2:
        print(f"{sys.argv[0]} image...")
        sys.exit(1)

    for filename in sys.argv[1:]:
        print(f"Reading {filename}...")

        img = Image.open(filename)
        img = img.resize((48, 48))

        with open(filename + '.icx', 'wb') as icx:
            for y in range(48):
                for x in range(48):
                    pixel = img.getpixel((x, y))
                    data = struct.pack('BBBB', *pixel)
                    icx.write(data)

        img.close()


if __name__ == '__main__':
    main()
