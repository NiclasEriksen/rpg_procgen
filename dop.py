from utils.ebs import World
import os
import random
import logging
from load_config import ConfigSectionMap as load_cfg
from collections import OrderedDict
import pyglet
import pymunk
from functions import center_image
from image_generator import grid_to_image
from components import *
from systems import *
from entities import *
from dungeon_generator import DungeonGenerator
pyglet.options['debug_gl'] = False

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

# GLOBAL VARIABLES
ROOT = os.path.dirname(__file__)
RES_PATH = os.path.join(ROOT, "resources")
PAUSED = False
FPS = 60.0               # Target frames per second

# Simple settings (temp)
keymap = {
    49: 1,
    50: 2,
    51: 3,
    52: 4,
    53: 5,
    54: 6,
    55: 7,
    56: 8,
    57: 9,
    48: 10,
}

# Get information about the OS and display #
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()

# Limit the frames per second to 30 #
pyglet.clock.set_fps_limit(FPS)


class GameWorld(World):
    def __init__(self):
        super().__init__()
        self.cfg = load_cfg("Game")
        # Initialize a window
        self.window = GameWindow()
        # Forward window events to gameworld
        self.window.on_mouse_motion = self.on_mouse_motion
        self.window.on_mouse_press = self.on_mouse_press
        self.window.on_mouse_scroll = self.on_mouse_scroll
        self.window.on_key_press = self.on_key_press
        self.window.on_resize = self.on_resize

        # Set default zoom
        self.zoom_factor = 2

        # Create batches and load textures
        self.batches = OrderedDict()
        self.load_textures()

        # Create a keyboard input handler for pyglet window
        self.input_keys = pyglet.window.key.KeyStateHandler()
        self.window.push_handlers(self.input_keys)

        # Setup dungeon configuration
        dungeon_cfg = load_cfg("Dungeon1")
        self.dungeon = DungeonGenerator(
            logger,
            dungeon_cfg
        )

        self.game_size = (
            dungeon_cfg["dungeon_size"][0] * 32,
            dungeon_cfg["dungeon_size"][1] * 32
        )

        self.dungeon.generate()

        logger.info("Generating dungeon graphics...")
        img_grid = self.dungeon.get_tilemap()

        grid_to_image(
            img_grid, "dungeon", self.game_size
        )

        dungeon_texture = self.load_single_texture(
            "dungeon"
        )
        dungeon_overlay_texture = self.load_single_texture(
            "dungeon_overlay"
        )

        self.bg = BG(self, dungeon_texture)
        self.fg = FG(self, dungeon_overlay_texture)
        self.bg.batch = Batch("dungeon")
        self.bg.batch.group = 0
        self.bg.position.set(0, 0)
        self.fg.batch = Batch("dungeon")
        self.fg.batch.group = 1
        self.fg.position.set(0, 0)

        logger.info("Setup physics space...")
        # Make physical space for physics engine
        self.phys_space = pymunk.Space()
        self.phys_space.damping = 0.001

        # Add entities to the world
        logger.info("Spawning enemies...")
        self.enemies = []
        for r in self.dungeon.enemy_rooms:
            for spawn in r.spawn_locations:
                x, y = spawn[0] * 32, spawn[1] * 32
                e = Enemy(self)
                e.position.set(x, y)
                self.enemies.append(e)

        logger.info("Generating wall rectangles...")
        self.wall_rects = self.dungeon.generate_wall_grid()
        self.walls = []
        for w in self.wall_rects:
            p1, p2 = w
            x = (p1[0] * 32)
            y = (p1[1] * 32)
            w = p2[0] * 32 - p1[0] * 32 + 32
            h = p2[1] * 32 - p1[1] * 32 + 32
            # print(p1, p2, x, y, w, h)
            wa = Wall(self)
            wa.physbody = PhysBody(shape="square", width=w, height=h)
            wa.position.set(x, y)
            self.walls.append(wa)

        logger.info("Placing collidable items...")
        # self.collidable = []
        # for c in self.dungeon.collidable:
        #     print(c.p1)
        #     co = Wall(self)
        #     co.physbody = PhysBody(shape="square", width=32, height=32)
        #     co.position.set(*c.p1)
        #     self.collidable.append(co)

        logger.info("Spawning player...")
        self.spawn_player()
        self.e = Enemy(self)
        self.e.position.set(self.p.position.x + 32, self.p.position.y)
        self.e.followtarget.who = self.p

        self.viewlines = []

    def spawn_player(self, point=(0, 0)):
        self.p = Player(self)
        c = self.dungeon.startroom.center
        x, y = c[0] * 32, c[1] * 32
        self.p.position.set(x, y)

    def load_textures(self):
        goblin_img = center_image(
            pyglet.image.load('resources/crappy_goblin.png')
        )
        player_body_img = center_image(
            pyglet.image.load('resources/player_body.png')
        )
        player_body_glow_img = center_image(
            pyglet.image.load('resources/player_body_glow.png')
        )
        wall_img = center_image(
            pyglet.image.load('resources/wall.png')
        )
        bg_img = center_image(
            pyglet.image.load('resources/bg.png')
        )

        self.textures = dict(
            enemy=goblin_img,
            player=player_body_img,
            player_glow=player_body_glow_img,
            wall=wall_img,
            bg=bg_img
        )

    def load_single_texture(self, name, center=False):
        if center:
            return center_image(
                pyglet.image.load(os.path.join(RES_PATH, name + '.png'))
            )
        else:
            return pyglet.image.load(os.path.join(RES_PATH, name + '.png'))

    def get_player(self):
        return self.p

    def get_gamepos(self, x, y):
        return int(x - self.window.offset_x), int(y - self.window.offset_y)

    def on_mouse_motion(self, x, y, dx, dy):
        pass
        # c = self.get_components(MouseControlled)
        # e = None
        # if c:
        #     try:
        #         e = self.get_entities(c[0])[0]
        #     except KeyError:
        #         pass

        # if e:
        #     e.mousecontrolled.x, e.mousecontrolled.y = self.get_gamepos(x, y)
        # print current mouse position
        # print(x, y)

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        self.update_ortho(width, height)
        # glMatrixMode(gl.GL_MODELVIEW)
        # glLoadIdentity()
        return pyglet.event.EVENT_HANDLED

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if scroll_y == 1 and self.zoom_factor < 5:
            self.zoom_factor += 0.5
        elif scroll_y == -1 and self.zoom_factor > 1:
            self.zoom_factor -= 0.5
        self.update_ortho(self.window.width, self.window.height)

    def update_ortho(self, w, h):
        lessen_w = int((w - (w / self.zoom_factor)) / 2)
        lessen_h = int(lessen_w * (h / w))

        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(lessen_w, w - lessen_w, lessen_h, h - lessen_h, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)
        glLoadIdentity()

    def on_mouse_press(self, x, y, button, modifiers):
        # pass
        # when a user presses a mouse button, print which one and mousepos
        print("{0} pressed at: {1},{2}.".format(button, x, y))
        p = self.get_player()
        p.mouseclicked = MouseClicked(button, *self.get_gamepos(x, y))

    def on_key_press(self, k, modifiers):
        if k == key.ESCAPE:
            # logger.info("Exiting...")
            pyglet.app.exit()

        if k == key._1:
            self.zoom_factor = 1
        if k == key._2:
            self.zoom_factor = 2
        if k == key._3:
            self.zoom_factor = 3

        if k == key.F2:
            e = [None]
            c = self.get_components(Input)
            for comp in c:
                e = self.get_entities(comp)

            if e[0] == self.p:
                delattr(self.p, "input")
                self.e.input = Input()
            elif e[0] == self.e:
                delattr(self.e, "input")
                self.p.input = Input()

        if k == key.F3:
            if getattr(self.e, "physbody"):
                delattr(self.e, "physbody")
            else:
                self.e.physbody = PhysBody()

        if k == key.F4:
            if getattr(self.p, "staticposition"):
                delattr(self.p, "staticposition")
                self.p.windowposition = WindowPosition()
            else:
                self.p.staticposition = StaticPosition(x=640, y=360)
                self.window.offset_x = 640 - self.p.position.x
                self.window.offset_y = 360 - self.p.position.y
                delattr(self.p, "windowposition")

        if k == key.F5:
            if getattr(self.p, "lightsource"):
                delattr(self.p, "lightsource")
            else:
                self.p.lightsource = LightSource()

        c = self.get_components(KeyboardControlled)
        e = None
        if c:
            try:
                e = self.get_entities(c[0])[0]
            except KeyError:
                pass

        if e:
            if getattr(e, "activeabilities"):
                try:
                    print(e.activeabilities.slots[keymap[k]])
                except KeyError:
                    # print("No ability defined for that key.")
                    pass


class GameWindow(pyglet.window.Window):  # Main game window

    def __init__(self):
        # Template for multisampling
        gl_template = pyglet.gl.Config(
            sample_buffers=1,
            samples=2,
            alpha_size=8,
            stencil_size=8
            )
        try:  # to enable multisampling
            gl_config = screen.get_best_config(gl_template)
        except pyglet.window.NoSuchConfigException:
            gl_template = pyglet.gl.Config(alpha_size=8)
            gl_config = screen.get_best_config(gl_template)
        gl_context = gl_config.create_context(None)
        super(GameWindow, self).__init__(
            context=gl_context,
            config=gl_config,
            resizable=False,
            vsync=True,
            )
        if not self.fullscreen:
            self.set_location(
                (screen.width - 1280) // 2,
                (screen.height - 720) // 2
            )
            self.width, self.height = 1280, 720

        self.offset_x, self.offset_y = 640, 360


if __name__ == "__main__":
    # Initialize world
    appworld = GameWorld()

    # Add component types
    # appworld.add_componenttype(KeyboardControl)

    # Add systems to the world to be processed in that order.
    # appworld.add_system(KeyboardHandling(appworld))
    appworld.add_system(InitializeEffectiveStatsSystem(appworld))
    appworld.add_system(ApplyAttributeStatsSystem(appworld))
    appworld.add_system(ApplyHPSystem(appworld))
    appworld.add_system(ApplyStaminaSystem(appworld))
    appworld.add_system(ApplyManaSystem(appworld))
    appworld.add_system(ApplyBasicAttackSystem(appworld))
    appworld.add_system(ApplyMovementSpeedSystem(appworld))
    appworld.add_system(LevelUpSystem(appworld))
    appworld.add_system(MobNamingSystem(appworld))
    appworld.add_system(GlowBatchSystem(appworld))
    appworld.add_system(SpriteBatchSystem(appworld))
    appworld.add_system(InputMovementSystem(appworld))
    appworld.add_system(HeadBobbingSystem(appworld))
    appworld.add_system(MoveSystem(appworld))
    appworld.add_system(FollowSystem(appworld))
    appworld.add_system(PhysicsSystem(appworld))
    appworld.add_system(TargetMobSystem(appworld))
    appworld.add_system(StaticSpritePosSystem(appworld))
    appworld.add_system(StaticGlowEffectPosSystem(appworld))
    appworld.add_system(WindowPosSystem(appworld))
    appworld.add_system(SpritePosSystem(appworld))
    appworld.add_system(GlowPosSystem(appworld))
    appworld.add_system(PulseAnimationSystem(appworld))
    appworld.add_system(CleanupClickSystem(appworld))
    appworld.add_system(LightingSystem(appworld))
    appworld.add_system(RenderSystem(appworld))

    # Schedule the update function on the world to run every frame.
    pyglet.clock.schedule_interval(appworld.process, 1.0 / FPS)

    # Initialize pyglet app
    pyglet.app.run()
