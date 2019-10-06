import os
import struct
import sys

import ujson
import utime

import buttons
import display


### DEFAULT SETTINGS

DEFAULT_BG = (0x00, 0x00, 0x00)
DEFAULT_FG = (0xFF, 0xFF, 0xFF)

### DEFAULT SETTINGS END


TIMEOUT = 0x100


# NOTE: This is basically a copy from simple_menu. However, plans are to support "tapping" interface...
def button_events(timeout=None):
    yield 0

    v = buttons.read(buttons.BOTTOM_LEFT | buttons.BOTTOM_RIGHT | buttons.TOP_RIGHT)
    button_pressed = True if v != 0 else False

    if timeout is not None:
        timeout = int(timeout * 1000)
        next_tick = utime.time_ms() + timeout

    while True:
        if timeout is not None:
            current_time = utime.time_ms()
            if current_time > next_tick:
                next_tick = current_time + timeout
                yield TIMEOUT

            v = buttons.read(buttons.BOTTOM_LEFT | buttons.BOTTOM_RIGHT | buttons.TOP_RIGHT)

            if v == 0:
                button_pressed = False

            elif not button_pressed:
                for mask in (buttons.BOTTOM_LEFT, buttons.BOTTOM_RIGHT, buttons.TOP_RIGHT):
                    if v & mask != 0:
                        yield mask


class Icon:
    """
    ICX icons are 48x48 pixel stored as (r,g,b,a) one byte each, row by row. Icons are loaded on-demand to keep
    memory usage low. At least 3 icons fit into memory right now...
    """

    def __init__(self, filename):
        self.filename = filename
        self.data = None

    def draw(self, d, bg, offset):
        """
        Draw icon an icon. The icon will be loaded and pre-rendered with the given background if data is not ready.

        :param d: Display to draw on.
        :param bg: Background color (used only if icon is not loaded).
        :param offset: X offset to draw icon at.
        """
        if self.data is None:
            self.data = self.load_icx(self.filename, bg)

        if self.data is None:
            return

        i = 0
        for y in range(48):
            for x in range(48):
                rgb = self.data[i:i + 3]
                i += 3
                if x + offset >= 0 and x + offset < 160:
                    d.pixel(x + offset, y + 4, col=rgb)

    @staticmethod
    def _read_icx(icx, bg):
        icx_data = []

        for y in range(48):
            for x in range(48):
                *rgb, alpha = struct.unpack('BBBB', icx.read(4))
                rate = alpha / 0xFF
                inv = 1 - rate
                icx_data += [int(bg_i * inv + rgb_i * rate)
                             for bg_i, rgb_i in zip(bg, rgb)]

        return icx_data

    @staticmethod
    def load_icx(filename, bg):
        """
        Load an ICX file and pre-render it with the given background color.

        :param filename: Path to ICX file.
        :param bg: Background used for rendering.
        :return: Image data (48 x 48 rgb data as linear buffer). Returns None if out of memory.
        """
        try:
            with open(filename, 'rb') as icx:
                icx_data = Icon._read_icx(icx, bg)

        except OSError:
            with open('/apps/menu/{}'.format(filename), 'rb') as icx:
                icx_data = Icon._read_icx(icx, bg)

        except MemoryError:
            return None

        return icx_data


class App:
    """
    Base class for application. Uses 'py.png.icx' as default icon.
    """

    default_icon = Icon('py.icx')

    def __init__(self, path, name=None, icon=None, **kwargs):
        """
        Create a new application.

        :param path: Path to the executable.
        :param name: Name to display in menu (opt.).
        :param icon: Icon to display in menu (opt.).
        """
        self.path = path
        self.name = name or path
        self.icon = self.default_icon if icon is None else Icon(icon)

    def start(self):
        """
        Run the application.
        """
        print("Running", self.path)
        os.exec(self.path)

    @staticmethod
    def all():
        """
        Discover all applications in '/apps' (and '/main.py' as home app). If present, 'metadata.json' will be read.

        :return: All discovered applications.
        """
        for f in os.listdir('/'):
            if f == 'main.py':
                yield PythonApp(f, name='Home', icon="home.icx")

        for f in sorted(os.listdir('/apps')):
            if f.endswith('.py'):
                yield PythonApp('/apps/{}'.format(f), name=f[:-3])

            elif f.endswith('.elf'):
                yield L0adableApp('/apps/{}'.format(f), name=f[:-4])

            else:
                try:
                    with open('/apps/{}/metadata.json'.format(f)) as meta:
                        info = ujson.load(meta)
                except Exception as e:
                    info = {}

                if 'name' not in info:
                    info['name'] = f

                if 'icon' in info:
                    info['icon'] = '/apps/{}/{}'.format(f, info['icon'])
                else:
                    # Check if icon is present.
                    try:
                        fp = open('/apps/{}/icon.icx'.format(f), 'rb')
                        fp.close()
                        info['icon'] = '/apps/{}/icon.icx'.format(f)
                    except Exception as e:
                        pass

                app_bin = info.get('bin', '__init__.py')
                if app_bin.endswith('.py'):
                    yield PythonApp('/apps/{}/{}'.format(f, app_bin), **info)
                elif app_bin.endswith('.elf'):
                    yield L0adableApp('/apps/{}/{}'.format(f, app_bin), **info)
                else:
                    yield App('/apps/{}/{}'.format(f, app_bin), **info)


class PythonApp(App):
    pass


class L0adableApp(App):
    default_icon = Icon('l0adable.icx')


class Menu:
    """
    Generate the menu.
    """

    def __init__(self, bg=None, fg=None):
        self.bg = bg or DEFAULT_BG
        self.fg = fg or DEFAULT_FG

        apps = list(App.all())
        # Add one overhang to always have prev/next item.
        self.apps = [apps[-1]] + apps + [apps[0]]
        self.curr = 1

        # Keep track of long name marqee.
        self.cycle = 0

    def error(self, d, e):
        """
        Display an error message and display it for a short while.

        :param d: Display to draw on.
        :param e: Exception that occured.
        """
        d.clear(self.bg)
        d.print(self.apps[self.curr].name, fg=self.fg, posx=4, posy=4, font=display.FONT16)
        d.print(str(e), fg=self.fg, posx=4, posy=24, font=display.FONT16)
        d.update()
        utime.sleep_ms(1200)

    def draw_curr(self, d):
        """
        Draw the current selected menu item.

        :param d: Display to draw on.
        """
        d.clear(self.bg)
        for icon, offset in zip([app.icon for app in self.apps[self.curr - 1:self.curr + 2]],
                                [-24, 56, 136]):
            icon.draw(d, self.bg, offset)

        name = self.apps[self.curr].name
        if len(name) > 12:
            delta = len(name) - 11
            name = name[self.cycle:self.cycle + 12]
            self.cycle = (self.cycle + 1) % delta

        posx = (160 - len(name) * 11) // 2
        d.print(name, fg=self.fg, posx=posx, posy=56, font=display.FONT16)
        d.update()

    def go_next(self, d):
        """ Select next menu item with animation. """
        self.apps[self.curr - 1].icon.data = None

        self.curr += 1
        if self.curr > len(self.apps) - 2:
            self.curr = 1

        icons = [self.apps[self.curr - 1].icon, self.apps[self.curr].icon, self.apps[self.curr + 1].icon]
        self._animate(d, icons, 56, -24)

        self.cycle = 0
        self.draw_curr(d)

    def go_prev(self, d):
        """ Select previous menu item with animation. """
        self.apps[self.curr + 1].icon.data = None

        self.curr -= 1
        if self.curr < 1:
            self.curr = len(self.apps) - 2

        icons = [self.apps[self.curr - 1].icon, self.apps[self.curr].icon, self.apps[self.curr + 1].icon]
        self._animate(d, icons, -104, 24)

        self.cycle = 0
        self.draw_curr(d)

    def _animate(self, d, icons, start, delta):
        offset = start + delta
        for _ in range(3):
            d.clear(self.bg)
            icons[0].draw(d, self.bg, offset)
            icons[1].draw(d, self.bg, offset + 80)
            icons[2].draw(d, self.bg, offset + 160)
            d.update()

            offset += delta

    def run_curr(self, d):
        """ (Try to) Start the current selected app. """
        d.clear().update()
        d.close()

        # Clear memory.
        self.apps[self.curr - 1].icon.data = None
        self.apps[self.curr].icon.data = None
        self.apps[self.curr + 1].icon.data = None

        # Try to execute app.
        try:
            self.apps[self.curr].start()

        except OSError as e:
            sys.print_exception(e)

            d = d.open()
            self.error(d, e)

    def run(self):
        """ Main loop: Read buttons and react on them. """
        try:
            d = display.open()

            d.clear(self.bg)
            d.print("Loading...", fg=self.fg, posx=25, posy=56, font=display.FONT16)
            d.update()

            self.draw_curr(d)

            while True:
                for evt in button_events(0.5):
                    if evt == TIMEOUT:
                        self.draw_curr(d)
                    elif evt == buttons.BOTTOM_LEFT:
                        self.go_prev(d)
                    elif evt == buttons.BOTTOM_RIGHT:
                        self.go_next(d)
                    elif evt == buttons.TOP_RIGHT:
                        self.run_curr(d)

        except KeyboardInterrupt:
            pass


def main():
    menu = Menu()
    menu.run()


main()
