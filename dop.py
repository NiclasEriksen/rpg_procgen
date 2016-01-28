from utils.ebs import World
import os
import random
from collections import OrderedDict
import pyglet
import pymunk
from functions import center_image
from components import *
from systems import *
from entities import *
pyglet.options['debug_gl'] = False


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
        # Initialize a window
        self.window = GameWindow()
        # Forward window events to gameworld
        self.window.on_mouse_motion = self.on_mouse_motion
        self.window.on_mouse_press = self.on_mouse_press
        self.window.on_key_press = self.on_key_press

        # Create batches and load textures
        self.batches = OrderedDict()
        self.load_textures()

        # Create a keyboard input handler for pyglet window
        self.input_keys = pyglet.window.key.KeyStateHandler()
        self.window.push_handlers(self.input_keys)

        # Make physical space for physics engine
        self.phys_space = pymunk.Space()
        self.phys_space.damping = 0.001

        # Add entities to the world
        self.e = Enemy(self)
        self.enemies = []
        for i in range(10):
            e = Enemy(self)
            e.position.set(
                random.randrange(20, 1000), random.randrange(20, 700)
            )
            self.enemies.append(e)

        self.spawn_player()
        self.e.followtarget.who = self.p

    def spawn_player(self, point=(0, 0)):
        # self.player = Mage(
        #     self, window=self.window,
        #     x=point[0], y=point[1]
        # )

        self.p = Player(self)
        # if hasattr(self.p, "input"):
        #     delattr(self.p, "input")
        # delattr(self.p, "input")
        # self.window.set_offset(
        #     self.player.windowpos[0] - self.player.x,
        #     self.player.windowpos[1] - self.player.y,

        # )

    def load_textures(self):
        goblin_img = center_image(
            pyglet.image.load('resources/crappy_goblin.png')
        )
        player_body_img = center_image(
            pyglet.image.load('resources/player_body.png')
        )

        self.textures = dict(
            enemy=goblin_img,
            player=player_body_img,
        )

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
            alpha_size=8
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
    appworld.add_system(SpriteBatchSystem(appworld))
    appworld.add_system(InputMovementSystem(appworld))
    appworld.add_system(MoveSystem(appworld))
    appworld.add_system(FollowSystem(appworld))
    appworld.add_system(PhysicsSystem(appworld))
    appworld.add_system(TargetMobSystem(appworld))
    appworld.add_system(StaticSpritePosSystem(appworld))
    appworld.add_system(WindowPosSystem(appworld))
    appworld.add_system(SpritePosSystem(appworld))
    appworld.add_system(CleanupClickSystem(appworld))
    appworld.add_system(RenderSystem(appworld))

    # Schedule the update function on the world to run every frame.
    pyglet.clock.schedule_interval(appworld.process, 1.0 / FPS)

    # Initialize pyglet app
    pyglet.app.run()
