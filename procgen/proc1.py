from collections import OrderedDict
import logging
import os
import random
import math
from functions import *
import pyglet
pyglet.options['debug_gl'] = False


# GLOBAL VARIABLES
ROOT = os.path.dirname(__file__)
RES_PATH = os.path.join(ROOT, "resources")
SCREENRES = (1440, 900)  # The resolution for the game window
CELL_SIZE = 4
VSYNC = True             # Vertical sync
PAUSED = False
FPS = 20.0               # Target frames per second

# Get information about the OS and display #
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()

# Limit the frames per second to 30 #
pyglet.clock.set_fps_limit(FPS)

# Logging
logging.basicConfig(
    filename='debug.log',
    filemode='w',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)


class Room:

    def __init__(self, x, y, w, h):
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + w, y + h
        self.w, self.h = w, h
        self.center = (
            math.floor((self.x1 + self.x2) / 2),
            math.floor((self.y1 + self.y2) / 2)
        )

    def check_intersect(self, room):
        if (
            (self.x1 <= room.x2) and
            (self.x2 >= room.x1) and
            (self.y1 <= room.y2) and
            (self.y2 >= room.y1)
        ):
            return True
        else:
            return False

    def draw(self):
        for gx in range(self.x1, self.x2):
            for gy in range(self.y1, self.y2):
                rect = create_rect(
                    *get_windowpos(gx, gy), CELL_SIZE, CELL_SIZE
                )
                # print(rect)
                pyglet.graphics.draw(
                    4, pyglet.gl.GL_QUADS, (
                        'v2i', rect
                    )
                )


class Corridor:

    def __init__(self, p1, p2, w=1):
        if p1[0] > p2[0] or p1[1] > p2[1]:
            self.x1, self.y1 = p2
            self.x2, self.y2 = p1
        else:
            self.x1, self.y1 = p1
            self.x2, self.y2 = p2
        if self.x1 == self.x2:
            self.orientation = "v"
            self.x2 += w - 1
        elif self.y1 == self.y2:
            self.orientation = "h"
            self.y2 += w - 1
        else:
            raise Exception("Line has to be straight.")

    def check_intersect(self, structure):
        if (
            (self.x1 <= structure.x2) and
            (self.x2 >= structure.x1) and
            (self.y1 <= structure.y2) and
            (self.y2 >= structure.y1)
        ):
            return True
        else:
            return False

    def draw(self):
        # if self.orientation == "v":
        #     x1, x2 = self.x1, self.x2
        # else:
        #     x1, x2 = self.x1, self.x2
        # if self.orientation == "h":
        #     y1, y2 = self.y1, self.y1
        # else:
        #     y1, y2 = self.y1, self.y2
        x1, x2 = self.x1, self.x2
        y1, y2 = self.y1, self.y2
        for gx in range(x1, x2 + 1):
            for gy in range(y1, y2 + 1):
                rect = create_rect(
                    *get_windowpos(gx, gy), CELL_SIZE, CELL_SIZE
                )
                pyglet.graphics.draw(
                    4, pyglet.gl.GL_QUADS, (
                        'v2i', rect
                    )
                )


class POI:

    def __init__(self, x, y, size=CELL_SIZE, color="green"):
        self.x, self.y = x, y
        self.size = size
        self.color = color

    def draw(self):
        rect = create_rect(
        *get_windowpos(self.x, self.y), self.size, self.size
        )
        pyglet.gl.glColor4f(*lookup_color(self.color, gl=True))
        pyglet.graphics.draw(
            4, pyglet.gl.GL_QUADS, (
                'v2i', rect
            )
        )


class DungeonGenerator:

    def __init__(self, config):
        self.config = dict(
            roomcount=12,
            room_min_size=5,
            room_max_size=30,
            dungeon_size=(60, 40),
            treasure_chance=30,
            enemy_chance=70,
            corridor_min_width=1,
            corridor_max_width=2,
            corridor_wide_chance=30,
            attempts_max=200,
        )
        self.rooms = []
        self.corridors = []

    def generate(self):
        pass

    def flush(self):
        self.rooms = []
        self.corridors = []

    def connect_rooms(self, r1, r2):
        x1, y1 = r1.center
        x2, y2 = r2.center
        # 50/50 chance of starting horizontal or vertical
        if random.randint(0, 1):
            c1p1 = (x1, y1)
            c1p2 = (x2, y1)
            c2p1 = (x2, y1)
            c2p2 = (x2, y2)
        else:
            c1p1 = (x1, y1)
            c1p2 = (x1, y2)
            c2p1 = (x1, y2)
            c2p2 = (x2, y2)

        w = self.config["corridor_min_width"]
        if not random.randint(0, 2):
            w = self.config["corridor_max_width"]
        c1 = Corridor(c1p1, c1p2, w=w)
        c2 = Corridor(c2p1, c2p2, w=w)
        self.corridors.append(c1)
        self.corridors.append(c2)

    def place_rooms(self):
        min_roomsize = self.config["room_min_size"]
        max_roomsize = self.config["room_max_size"]
        map_width, map_height = self.config["dungeon_size"]
        poi = []
        i = 0
        attempts = 0
        while i < self.config["roomcount"]:
            if attempts > self.config["attempts_max"]:
                print("Failed to add more rooms")
                break
            w = random.randrange(min_roomsize, max_roomsize + 1)
            h = random.randrange(min_roomsize, max_roomsize + 1)
            x = random.randrange(0 + 1, map_width - w - 1)
            y = random.randrange(0 + 1, map_height - h - 1)
            newroom = Room(x, y, w, h)
            valid = True
            for r in self.rooms:
                if newroom.check_intersect(r):
                    valid = False
                    attempts += 1
                    break
            if valid:
                attempts = 0
                self.rooms.append(newroom)
                i += 1

        oldroom = None
        for r in self.rooms:
            if oldroom:
                self.connect_rooms(r, oldroom)
            oldroom = r

        available_rooms = self.rooms.copy()
        startroom = self.rooms[random.randrange(0, len(rooms))]
        available_rooms.remove(startroom)
        poi.append(POI(*startroom.center))
        while len(available_rooms):
            r = available_rooms[random.randrange(0, len(available_rooms))]
            if random.randint(0, 101) <= self.config["treasure_chance"]:
                newpoi = POI(*r.center, color="white")
            else:
                newpoi = POI(*r.center, color="blue")
            poi.append(newpoi)
            available_rooms.remove(r)

        print("Rooms created: " + str(len(self.rooms)))


def get_windowpos(x, y, square_size=CELL_SIZE):
    return x * square_size, y * square_size


def create_rect(x, y, w, h):
    return [
        x, y,
        x, y + h,
        x + w, y + h,
        x + w, y
    ]


def connect_rooms(r1, r2):
    corridors = []
    x1, y1 = r1.center
    x2, y2 = r2.center
    if random.randint(0, 1):
        c1p1 = (x1, y1)
        c1p2 = (x2, y1)
        c2p1 = (x2, y1)
        c2p2 = (x2, y2)
    else:
        c1p1 = (x1, y1)
        c1p2 = (x1, y2)
        c2p1 = (x1, y2)
        c2p2 = (x2, y2)

    w = 1
    if not random.randint(0, 2):
        w = 2
    c1 = Corridor(c1p1, c1p2, w=w)
    c2 = Corridor(c2p1, c2p2, w=w)
    corridors.append(c1)
    corridors.append(c2)
    return corridors


def place_rooms(max):
    min_roomsize = 6
    max_roomsize = 30
    map_width, map_height = SCREENRES[0] // CELL_SIZE, SCREENRES[1] // CELL_SIZE
    rooms = []
    corridors = []
    poi = []
    i = 0
    attempts = 0
    while i < max:
        if attempts > 200:
            print("Failed to add more rooms")
            break
        w = random.randrange(min_roomsize, max_roomsize + 1)
        h = random.randrange(min_roomsize, max_roomsize + 1)
        x = random.randrange(0 + 1, map_width - w - 1)
        y = random.randrange(0 + 1, map_height - h - 1)
        newroom = Room(x, y, w, h)
        valid = True
        for r in rooms:
            if newroom.check_intersect(r):
                valid = False
                attempts += 1
                break
        if valid:
            attempts = 0
            rooms.append(newroom)
            i += 1

    oldroom = None
    for r in rooms:
        if oldroom:
            for c in connect_rooms(r, oldroom):
                corridors.append(c)
        oldroom = r

    available_rooms = rooms.copy()
    startroom = rooms[random.randrange(0, len(rooms))]
    available_rooms.remove(startroom)
    poi.append(POI(*startroom.center))
    while len(available_rooms):
        r = available_rooms[random.randrange(0, len(available_rooms))]
        if random.randint(0, 2):
            newpoi = POI(*r.center, color="blue")
        else:
            newpoi = POI(*r.center, color="white")
        poi.append(newpoi)
        available_rooms.remove(r)


    print("Rooms created: " + str(len(rooms)))
    return rooms, corridors, poi


class GameWindow(pyglet.window.Window):  # Main game window

    def __init__(self):
        # Template for multisampling
        gl_template = pyglet.gl.Config(
            sample_buffers=1,
            samples=2,
            alpha_size=8
            )
        try:  # to enable multisampling
            gl_config = screen.get_best_config(gl_template)
        except pyglet.window.NoSuchConfigException:
            gl_template = pyglet.gl.Config(alpha_size=8)
            gl_config = screen.get_best_config(gl_template)
        logger.debug("Creating OpenGL context")
        gl_context = gl_config.create_context(None)
        logger.debug("Subclassing pyglet window, setting parameters.")
        super(GameWindow, self).__init__(
            context=gl_context,
            config=gl_config,
            resizable=False,
            vsync=VSYNC,
            fullscreen=False
            )
        if not self.fullscreen:
            logger.debug(
                "Not fullscreen, setting screen resolution to {0}x{1}.".format(
                    SCREENRES[0], SCREENRES[1]
                )
            )
            logger.debug("Centering window on screen.")
            self.set_location(
                (screen.width - SCREENRES[0]) // 2,
                (screen.height - SCREENRES[1]) // 2
            )
            self.width, self.height = SCREENRES[0], SCREENRES[1]

        self.debug = False
        self.logger = logger

    def update_offset(self, dx=False, dy=False):
        self.offset_x += dx
        self.offset_y += dy

    def set_offset(self, x, y):
        self.offset_x, self.offset_y = x, y

    def get_windowpos(self, x, y, check=False, tol=0, precise=False):
        if check:
            if (
                (x + self.offset_x > self.width + tol) or
                (x + self.offset_x < 0 - tol)
            ):
                return False
            if (
                (y + self.offset_y > self.height + tol) or
                (y + self.offset_y < 0 - tol)
            ):
                return False

        if precise:
            return x + self.offset_x, y + self.offset_y
        else:
            return int(x + self.offset_x), int(y + self.offset_y)

    def get_gamepos(self, x, y, check=False, tol=0):
        if check:
            if (
                (x - self.offset_x > self.width + tol) or
                (x - self.offset_x < 0 - tol)
            ):
                return False
            if (
                (y - self.offset_y > self.height + tol) or
                (y - self.offset_y < 0 - tol)
            ):
                return False

        return int(x - self.offset_x), int(y - self.offset_y)

    def on_key_press(self, symbol, modifiers):
        k = pyglet.window.key
        if symbol == k.ESCAPE:
            pyglet.app.exit()
        elif symbol == k.F12:
            self.debug = not self.debug
        elif symbol == k.G:
            rooms = random.randrange(8, 15)
            self.rooms, self.corridors, self.poi = place_rooms(rooms)

    def render(self, dt):
        # room1 = Room(0, 0, 5, 5)
        # room2 = Room(8, 0, 5, 5)
        # room3 = Room(4, 10, 5, 5)
        # cor1 = Corridor(room1.center, room2.center)
        # cor2 = Corridor((6, 3), (6, 12))
        pyglet.gl.glClearColor(*lookup_color("dgrey", gl=True))
        self.clear()
        pyglet.gl.glColor4f(*lookup_color("lgrey", gl=True))
        for r in self.rooms:
            r.draw()
        # pyglet.gl.glColor4f(*lookup_color("blue", gl=True))
        for c in self.corridors:
            c.draw()
        for p in self.poi:
            p.draw()
        # room1.draw()
        # room2.draw()
        # room3.draw()
        # cor1.draw()
        # cor2.draw()


if __name__ == "__main__":
    # Initialize game window
    w = GameWindow()
    w.rooms, w.corridors, w.poi = place_rooms(12)
    # print(room1.check_intersect(room2))
    pyglet.clock.schedule_interval(w.render, 1.0 / FPS)

    # Initialize pyglet app
    pyglet.app.run()
