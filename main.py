from collections import OrderedDict
import logging
import os
import random
import glob
import pyglet
import pymunk
pyglet.options['debug_gl'] = False


# GLOBAL VARIABLES
ROOT = os.path.dirname(__file__)
RES_PATH = os.path.join(ROOT, "resources")
PAUSED = False
FPS = 60.0               # Target frames per second

# Get information about the OS and display #
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()

# Limit the frames per second to 30 #
pyglet.clock.set_fps_limit(FPS)
fps_display = pyglet.clock.ClockDisplay()


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

logger.debug("Importing game modules...")
import items
from image_generator import grid_to_image
from load_config import ConfigSectionMap as load_cfg
from player import Player, Mage
from enemy import Enemy
from animations import Animator
from ui import UI
from functions import *
from dungeon_generator import DungeonGenerator
import spatial
logger.debug("Done.")


class Game:

    def __init__(self, window):
        self.window = window
        self.cfg = load_cfg("Game")

    def newgame(self, level):
        logger.info("Starting new game...")

        self.window.flush()

        dungeon_cfg = load_cfg("Dungeon2")
        self.dungeon = DungeonGenerator(
            logger,
            dungeon_cfg
        )

        self.game_size = (
            dungeon_cfg["dungeon_size"][0] * 32,
            dungeon_cfg["dungeon_size"][1] * 32
        )

        self.space = pymunk.Space()

        self.dungeon.generate()

        self.spatial_hash = spatial.SpatialHash()
        for w in self.dungeon.walls:
            self.spatial_hash.insert_object_for_rect(
                w.p1,
                w.p2,
                w
            )
        for c in self.dungeon.collidable:
            self.spatial_hash.insert_object_for_rect(
                c.p1,
                c.p2,
                c
            )

        logger.info("Generating dungeon graphics...")
        img_grid = self.dungeon.get_tilemap()

        grid_to_image(
            img_grid, "dungeon", self.game_size
        )

        dungeon_texture = self.window.load_single_texture(
            "dungeon"
        )
        dungeon_overlay_texture = self.window.load_single_texture(
            "dungeon_overlay"
        )

        self.dungeon_sprite = pyglet.sprite.Sprite(
                dungeon_texture,
                x=0, y=0,
                batch=self.window.batches["dungeon"]
            )
        self.dungeon_overlay_sprite = pyglet.sprite.Sprite(
                dungeon_overlay_texture,
                x=0, y=0,
                batch=self.window.batches["dungeon_overlay"]
            )

        logger.info("Done.")

        start = self.window.grid_to_window(*self.dungeon.startroom.center)
        # self.tiles = tiles.TiledRenderer(self.window, level)
        logger.info("Spawning player...")
        self.player = Mage(
            self, window=self.window,
            x=start[0], y=start[1]
        )

        # Player body for physics
        inertia = pymunk.moment_for_circle(10, 0, 12, (0, 0))
        body = pymunk.Body(10, inertia)
        body.position = (self.player.x, self.player.y)
        shape = pymunk.Circle(body, 12, (0, 0))
        shape.elasticity = 0.2
        # shape.collision_type = 1
        shape.group = 0
        self.space.add(body, shape)
        self.player.body = body
        logger.info("Done.")

        # Add a static square for every dungeon wall
        for w in self.dungeon.walls:
            body = pymunk.Body()
            body.position = w.center
            box_points = [(-16, -16), (-16, 16), (16, 16), (16, -16)]
            shape = pymunk.Poly(body, box_points, (0, 0))
            shape.group = 1
            self.space.add(shape)
            w.body = body
        for c in self.dungeon.collidable:
            body = pymunk.Body()
            body.position = c.center
            box_points = [(-16, -16), (-16, 16), (16, 16), (16, -16)]
            shape = pymunk.Poly(body, box_points, (0, 0))
            shape.group = 1
            self.space.add(shape)
            c.body = body

        # self.space.add_collision_handler(1, 1, post_solve=smack)
        self.space.damping = 0.001

        self.window.set_offset(
            self.player.windowpos[0] - self.player.x,
            self.player.windowpos[1] - self.player.y,

        )
        self.window.update_display_dungeon()

        itemlist = items.L1_Sword(), items.L1_Armor(), items.L1_Ring()
        for i in itemlist:
            self.player.equip_item(i)
        self.player.update_stats()
        self.player.restore_stats()

        logger.info("Spawning enemies...")
        self.enemies = []
        for r in self.dungeon.enemy_rooms:
            for spawn in r.spawn_locations:
                x, y = self.window.grid_to_window(*spawn)
                self.add_enemy(x, y)

        i = 0
        for e in self.enemies:
            e.modifiers["str"] += i
            e.update_stats()
            e.reset()
            i += 3
        logger.info("Done.")

        if self.window.ui:
            self.window.ui.add_stats(
                self.player, 0, self.window.height, 120, 240
            )

        logger.info("Game successfully loaded.")

    def add_enemy(self, x, y):
        inertia = pymunk.moment_for_circle(20, 0, 12, (0, 0))
        body = pymunk.Body(20, inertia)
        body.position = (x, y)
        shape = pymunk.Circle(body, 12, (0, 0))
        shape.group = 0
        shape.elasticity = 0.2
        self.space.add(body, shape)
        e = Enemy(self, window=self.window, x=x, y=y)
        e.name = self.generate_name("surname")
        e.body = body
        self.enemies.append(e)

    def generate_name(self, type):
        syllables = load_cfg("Syllables")[type]
        syllable_count = random.randrange(2, 5)
        surname, title_pre, title_post, i = "", "", "", 0
        while i < syllable_count:
            syl = random.choice(syllables)
            if syl not in surname:
                surname += syl
                i += 1
        if not random.randint(0, 4):
            tp = load_cfg("Syllables")["title_pre"]
            title_pre = random.choice(tp)
            tp = load_cfg("Syllables")["title_post"]
            title_post = random.choice(tp)
            if random.randint(0, 3):
                fullname = "{0} the {1}{2}".format(
                    surname.title(),
                    title_pre.title(),
                    title_post,
                )
            else:
                fullname = "{0} {1}{2}".format(
                    surname.title(),
                    title_pre.title(),
                    title_post,
                )
        elif not random.randint(0, 6):
            if random.randint(0, 1):
                tp = load_cfg("Syllables")["title_pre"]
            else:
                tp = load_cfg("Syllables")["title_post"]
            title_pre = random.choice(tp)
            if title_pre[0] == "-":
                title_pre = title_pre[1:]
            fullname = "{0} the {1}".format(
                surname.title(),
                title_pre.title(),
            )
        else:
            fullname = surname.title()

        if check_consecutive_letters(fullname, 3):
            self.generate_name("surname")
        else:
            return fullname

    def check_enemy_collision(self, x, y):
        for e in self.enemies:
            if check_point_rectangle(x, y, e.rectangle):
                return True
        else:
            return False

    def update_z_index(self):
        for e in self.enemies:
            if e.y > self.player.y:
                e.sprite.group = self.window.bg_group
            else:
                e.sprite.group = self.window.fg_group

    def update(self, dt):
        for x in range(10):
            self.space.step(dt / 10)
        if self.player:
            self.player.update(dt)
        if len(self.enemies) > 0:
            self.update_z_index()
            for e in self.enemies:
                e.update(dt)


class GameWindow(pyglet.window.Window):  # Main game window

    def __init__(self):
        # Load config from file
        self.cfg = load_cfg("Screen")
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
            vsync=self.cfg["vsync"],
            fullscreen=self.cfg["fullscreen"]
            )
        if not self.fullscreen:
            logger.debug(
                "Not fullscreen, setting screen resolution to {0}x{1}.".format(
                    self.cfg["width"], self.cfg["height"]
                )
            )
            logger.debug("Centering window on screen.")
            self.set_location(
                (screen.width - self.cfg["width"]) // 2,
                (screen.height - self.cfg["height"]) // 2
            )
            self.width, self.height = self.cfg["width"], self.cfg["height"]

        self.debug = False
        self.logger = logger
        self.fps_display = pyglet.clock.ClockDisplay()

        self.mouse_pos = (0, 0)
        self.selected_object = None

        logger.debug("Loading textures from folder \"{0}\".".format(RES_PATH))
        self.load_textures()
        self.load_animations()
        self.fg_group = pyglet.graphics.OrderedGroup(2)
        self.mid_group = pyglet.graphics.OrderedGroup(1)
        self.bg_group = pyglet.graphics.OrderedGroup(0)
        self.batches = OrderedDict()
        self.batches["gui0"] = pyglet.graphics.Batch()
        self.batches["gui1"] = pyglet.graphics.Batch()
        self.batches["gui2"] = pyglet.graphics.Batch()
        self.flush()

        self.offset_x, self.offset_y = 0, 0

        # GUI
        self.build_ui()

        self.load_map_files()

        self.game = Game(self)
        self.game.newgame(self.selected_mapfile)

        self.update_offset()

    def flush(self):
        self.batches["dungeon"] = pyglet.graphics.Batch()
        self.batches["dungeon_overlay"] = pyglet.graphics.Batch()
        self.batches["creatures"] = pyglet.graphics.Batch()
        self.batches["player"] = pyglet.graphics.Batch()
        self.batches["projectiles"] = pyglet.graphics.Batch()

    def load_textures(self):
        logger.info("Loading textures...")
        player_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'player.png'))
        )
        player_body_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'player_body.png'))
        )
        player_hand_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'player_hands.png'))
        )
        button_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'button.png'))
        )
        button_down_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'button_down.png'))
        )
        fireball_s_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'fireball_s.png'))
        )
        fireball_l_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'fireball_l.png'))
        )
        bolt_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'white_bolt.png'))
        )
        rc_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'red_circle.png'))
        )
        cursor_default_img = pyglet.image.load(
            os.path.join(RES_PATH, "cursors", "default.png")
        )
        cursor_projectile_img = pyglet.image.load(
            os.path.join(RES_PATH, "cursors", "projectile.png")
        )

        self.textures = dict(
            player=player_img,
            player_body=player_body_img,
            player_hand=player_hand_img,
            button=button_img,
            button_down=button_down_img,
            fireball1=fireball_s_img,
            fireball2=fireball_l_img,
            bolt=bolt_img,
            redcircle=rc_img,
        )

        self.reticules = dict(
            default=pyglet.window.ImageMouseCursor(cursor_default_img, 2, 32),
            projectile=pyglet.window.ImageMouseCursor(
                cursor_projectile_img, 20, 20
            ),
        )

        logger.info(
            "Done, {} textures loaded.".format(len(self.textures))
        )

    def load_single_texture(self, name, center=False):
        if center:
            return center_image(
                pyglet.image.load(os.path.join(RES_PATH, name + '.png'))
            )
        else:
            return pyglet.image.load(os.path.join(RES_PATH, name + '.png'))

    def get_texture(self, name):
        try:
            return self.textures[name]
        except KeyError:
            logger.debug("Texture \"{0}\" not found".format(name))
            return None

    def load_animations(self):
        logger.info("Loading animations...")
        self.animator = Animator(self)
        logger.info(
            "Finished loading {} animations.".format(
                len(self.animator.animations)
            )
        )
        # for key, value in self.animator.animations.items():
        #     print(key)

        logger.info("Loading player animations...")
        img = self.load_single_texture("player_sheet")
        player_anim_grid = pyglet.image.ImageGrid(img, 8, 6)

        for seq in player_anim_grid:
            seq = center_image(seq)

        down_anim_seq = reversed(player_anim_grid[42:48])
        down_static = player_anim_grid[(7, 4)]
        left_anim_seq = reversed(player_anim_grid[36:42])
        left_static = player_anim_grid[(6, 4)]
        right_anim_seq = reversed(player_anim_grid[30:36])
        right_static = player_anim_grid[(5, 4)]
        up_anim_seq = reversed(player_anim_grid[24:30])
        up_static = player_anim_grid[(4, 4)]
        ld_anim_seq = reversed(player_anim_grid[18:24])
        ld_static = player_anim_grid[(3, 4)]
        rd_anim_seq = reversed(player_anim_grid[12:18])
        rd_static = player_anim_grid[(2, 4)]
        lu_anim_seq = reversed(player_anim_grid[6:12])
        lu_static = player_anim_grid[(1, 4)]
        ru_anim_seq = reversed(player_anim_grid[0:6])
        ru_static = player_anim_grid[(0, 4)]
        down_anim = pyglet.image.Animation.from_image_sequence(
            down_anim_seq, 0.2, True
        )
        left_anim = pyglet.image.Animation.from_image_sequence(
            left_anim_seq, 0.2, True
        )
        right_anim = pyglet.image.Animation.from_image_sequence(
            right_anim_seq, 0.2, True
        )
        up_anim = pyglet.image.Animation.from_image_sequence(
            up_anim_seq, 0.2, True
        )
        ld_anim = pyglet.image.Animation.from_image_sequence(
            ld_anim_seq, 0.2, True
        )
        rd_anim = pyglet.image.Animation.from_image_sequence(
            rd_anim_seq, 0.2, True
        )
        lu_anim = pyglet.image.Animation.from_image_sequence(
            lu_anim_seq, 0.2, True
        )
        ru_anim = pyglet.image.Animation.from_image_sequence(
            ru_anim_seq, 0.2, True
        )
        self.player_anim_grid = dict(
            down=down_anim,
            left=left_anim,
            right=right_anim,
            up=up_anim,
            leftdown=ld_anim,
            rightdown=rd_anim,
            leftup=lu_anim,
            rightup=ru_anim
        )
        self.player_static_img = dict(
            down=down_static,
            left=left_static,
            right=right_static,
            up=up_static,
            leftdown=ld_static,
            rightdown=rd_static,
            leftup=lu_static,
            rightup=ru_static
        )
        logger.info("Finished loading player animations.")

    def get_anim(self, name):
        try:
            return self.animator.get_anim(name)
        except KeyError:
            logger.error("No animation by name {} found".format(name))

    def load_map_files(self):
        self.maplist = sorted(glob.glob(os.path.join(RES_PATH, '*.tmx')))
        try:
            self.selected_mapfile = self.maplist[0]
        except IndexError:
            logger.error("No map files found!")
            self.selected_mapfile = None

    def set_reticule(self, reticule):
        if reticule == "projectile":
            self.set_mouse_cursor(self.reticules["projectile"])
        else:
            self.set_mouse_cursor(self.reticules["default"])

    def build_ui(self):
        self.ui = UI(self)
        self.ui.add_button(
            self.width - 32, self.height - 16, text="Exit",
            cb=pyglet.app.exit
        )
        self.ui.add_bar(
            self.width - 100, 50,
            text="Health", width=200, height=20,
            color="red", shows="hp"
        )
        self.ui.add_bar(
            self.width - 100, 30,
            text="Stamina", width=200, height=20,
            color="green", shows="sta"
        )
        self.ui.add_bar(
            self.width - 100, 10,
            text="Mana", width=200, height=20,
            color="blue", shows="mp"
        )
        pyglet.clock.schedule_interval(self.ui.update, 1.0 / FPS)

    def update_offset(self, dx=False, dy=False):
        self.offset_x += dx
        self.offset_y += dy
        self.update_display_dungeon()

    def set_offset(self, x, y):
        self.offset_x, self.offset_y = x, y
        self.update_display_dungeon()

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

    def grid_to_window(self, x, y):
        return x * 32, y * 32

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

    def on_mouse_press(self, x, y, button, modifiers):
        p = self.game.player
        gamepos = self.get_gamepos(x, y)
        if button == 1:
            if self.ui.check(x, y):  # Checks if mouse press is on ui elements
                logger.debug("Button hit, not registering presses on grid.")
            else:   # if its not, handle presses as usual
                if p.actions["targeting"]:
                    if (
                        p.actions["targeting"].use(
                            target=self.get_gamepos(x, y)
                        )
                    ):
                        p.clear_ability_target()
                elif p and len(self.game.enemies) > 0:
                    for e in self.game.spatial_hash.get_objects_from_point(
                        gamepos, radius=32, type=Enemy
                    ):
                        if get_dist(e.x, e.y, *gamepos) <= 24:
                            p.set_target(e)
                            break
                    else:
                        p.clear_target()

        if button == 4:
            if self.ui.check(x, y, dry=True):
                pass
            elif p:
                p.clear_ability_target()
                if len(self.game.enemies) > 0:
                    for e in self.game.spatial_hash.get_objects_from_point(
                        gamepos, radius=32, type=Enemy
                    ):
                        if get_dist(e.x, e.y, *gamepos) <= 24:
                            p.auto_attack_target = e
                            p.set_target(e)
                            break
                    else:
                        p.clear_target()

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        if button == 1:
            if self.ui.check(x, y, press=False):
                pass

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)

    def on_key_press(self, symbol, modifiers):
        k = pyglet.window.key
        if symbol == k.ESCAPE:
            logger.info("Exiting...")
            pyglet.app.exit()
        elif symbol == k.F12:
            self.debug = not self.debug
        elif symbol == k.F5:
            self.game.newgame(self.selected_mapfile)
        elif symbol == k.F2:
            self.game.add_enemy(*self.get_gamepos(*self.mouse_pos))
        if self.game.player:
            if symbol == k.W:
                self.game.player.move_dir["up"] = True
            elif symbol == k.A:
                self.game.player.move_dir["left"] = True
            elif symbol == k.S:
                self.game.player.move_dir["down"] = True
            elif symbol == k.D:
                self.game.player.move_dir["right"] = True

            if symbol == k.F1:
                for i in range(50):
                    self.game.player.levelup(attribute="str")
                    self.game.player.levelup(attribute="agi")
                    self.game.player.levelup(attribute="int")

            if symbol == k.LSHIFT:
                self.game.player.actions["sprint"] = True

            # Cast abilitites
            target = self.get_gamepos(*self.mouse_pos)
            if symbol == k._1:
                self.game.player.use_ability(1, target=target)
            if symbol == k._2:
                self.game.player.use_ability(2, target=target)
            if symbol == k._3:
                self.game.player.use_ability(3, target=target)
            if symbol == k._4:
                self.game.player.use_ability(4, target=target)

            # Level up attributes
            if symbol == k.EXCLAMATION:
                self.game.player.levelup(attribute="str")
            if symbol == k.DOUBLEQUOTE:
                self.game.player.levelup(attribute="agi")
            if symbol == k.HASH:
                self.game.player.levelup(attribute="int")

    def on_key_release(self, symbol, modifiers):
        k = pyglet.window.key
        if self.game.player:
            if symbol == k.W:
                self.game.player.move_dir["up"] = False
            elif symbol == k.A:
                self.game.player.move_dir["left"] = False
            elif symbol == k.S:
                self.game.player.move_dir["down"] = False
            elif symbol == k.D:
                self.game.player.move_dir["right"] = False
            if symbol == k.LSHIFT:
                self.game.player.actions["sprint"] = False

    def update_display_dungeon(self):
        x, y = int(self.offset_x), int(self.offset_y)
        self.game.dungeon_sprite.x = x
        self.game.dungeon_sprite.y = y
        self.game.dungeon_overlay_sprite.x = x
        self.game.dungeon_overlay_sprite.y = y

    def update(self, dt):
        if self.game:
            self.game.update(dt)

    def render(self, dt):
        pyglet.gl.glClearColor(*lookup_color("dgrey", gl=True))
        self.clear()
        self.batches["dungeon"].draw()
        self.batches["gui0"].draw()
        self.batches["creatures"].draw()

        self.batches["player"].draw()
        self.batches["projectiles"].draw()
        if hasattr(self, "animator"):
            self.animator.render()
        self.batches["dungeon_overlay"].draw()

        # enemy_count = pyglet.text.Label(
        #     text=str(len(self.game.enemies)), font_name=None, font_size=18,
        #     x=50, y=400, anchor_x="left", anchor_y="top",
        #     color=lookup_color("black")
        # )
        # enemy_count.draw()
        self.ui.draw()


if __name__ == "__main__":
    # Initialize game window
    w = GameWindow()
    w.set_reticule("default")
    pyglet.clock.schedule_interval(w.render, 1.0 / FPS)
    pyglet.clock.schedule_interval(w.update, 1.0 / FPS)

    # Initialize pyglet app
    pyglet.app.run()
