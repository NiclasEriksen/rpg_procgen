from brain import Brain
from functions import get_dist, rotate2d, get_diag_ratio
from random import randrange
from dungeon_generator import Collidable
from pyglet.sprite import Sprite
import math


class Movement:

    def __init__(self, owner, speed=0, max_speed=800, target=None):
        self.owner = owner
        self.speed = speed
        self.max_speed = max_speed
        self.target = target

    def set_pos(self, pos):
        self.owner.x, self.owner.y = pos[0], pos[1]
        self.owner.body.position = pos[0], pos[1]

    def update(self, dt):
        ms = self.speed
        if ms > self.max_speed:
            ms = self.max_speed

        if self.target:
            velx = self.target[0] - self.owner.x
            vely = self.target[1] - self.owner.y
            if hasattr(self.owner, "body"):
                self.owner.body.velocity.x += velx / 10
                self.owner.body.velocity.y += vely / 10
            else:
                print("No procedure for that yet.")

        if hasattr(self.owner, "body"):
            if hasattr(self.owner, "move_dir"):
                d = self.owner.move_dir
                if (d["up"] or d["down"]) and not (d["up"] == d["down"]):
                    if (
                        (d["left"] or d["right"]) and not
                        (d["left"] == d["right"])
                    ):
                        ms /= get_diag_ratio()  # Reduces ms if diagonal

                if d["up"] and not d["down"]:
                    if self.owner.body.velocity.y < ms:
                        self.owner.body.velocity.y += ms * 5 * dt

                if d["down"] and not d["up"]:
                    if self.owner.body.velocity.y > -ms:
                        self.owner.body.velocity.y -= ms * 5 * dt

                if d["left"] and not d["right"]:
                    if self.owner.body.velocity.x > -ms:
                        self.owner.body.velocity.x -= ms * 5 * dt

                if d["right"] and not d["left"]:
                    if self.owner.body.velocity.x < ms:
                        self.owner.body.velocity.x += ms * 5 * dt
            self.owner.x, self.owner.y = self.owner.body.position


class Actor:

    def __init__(self):
        self.brain = Brain()
        self.movement = Movement(self, max_speed=800)
        self.max_velocity = 800
        self.move_target = None
        self.attack_target = None
        self.brain.push_state(self.ai_idle)

    def remove_body(self):
        try:
            for s in self.body.shapes:
                self.game.space.remove(s)
            self.game.space.remove(self.body)
        except:
            print("Something fucky with physics.")

    def ai_wander(self):
        if self.body:
            self.body.apply_impulse(
                (randrange(-2500, 2500), randrange(-2500, 2500))
            )
            self.brain.pop_state()

    def ai_move_to_target(self, *args, **kwargs):
        mt = self.move_target
        if mt:
            d = get_dist(
                mt.x,
                mt.y,
                self.x,
                self.y
            )
            if d > self.get_stat("arng"):
                line_of_sight = True
                line = (
                    (self.x, self.y), (mt.x, mt.y)
                )
                raycast_objects = self.game.spatial_hash.get_objects_from_line(
                    *line,
                    type=Collidable
                )
                for o in raycast_objects:
                    for s in o.body.shapes:
                        if s.segment_query(*line):
                            line_of_sight = False
                            break
                if line_of_sight:
                    self.movement.target = (mt.x, mt.y)
                else:
                    self.movement.target = None
                    self.brain.pop_state()
            else:
                self.brain.pop_state()
        else:
            self.brain.pop_state()

    def ai_feared(self, *args, **kwargs):
        pass

    def ai_attack(self):
        if self.attack_target:
            if self.attack_target.hp <= 0:
                self.brain.pop_state()
                self.attack_target = None
                self.auto_attack_target = None
            else:
                d = get_dist(
                    self.attack_target.x,
                    self.attack_target.y,
                    self.x,
                    self.y
                )
                if d < 40:
                    if not self.auto_attack_target:
                        self.auto_attack_target = self.attack_target
                else:
                    self.move_target = self.attack_target
                    self.brain.push_state(self.ai_move_to_target)
        else:
            self.brain.pop_state()

    def ai_idle(self):
        if self.game.player:
            d = get_dist(
                self.game.player.x,
                self.game.player.y,
                self.x,
                self.y
            )
            if d <= 100:
                self.attack_target = self.game.player
                self.brain.push_state(self.ai_attack)
        else:
            self.move_target = None
            self.attack_target = None
            self.auto_attack_target = None


class Limb:

    def __init__(self):
        self.offset = 0, 0
        self.glow_color = (255, 255, 255)
        self.glow_opacity = 255


class Hand(Limb):

    def __init__(
        self, body, relative_position, texture,
        glow_texture=None, glow_color=None
    ):
        super().__init__()
        self.body_pos = relative_position
        self.body = body
        self.sprite = Sprite(
            texture,
            x=body.sprite.x + relative_position[0],
            y=body.sprite.y + relative_position[1],
            batch=body.sprite.batch, group=body.window.mid_group
        )
        if glow_texture:
            self.glow = Sprite(
                glow_texture,
                x=body.sprite.x + relative_position[0],
                y=body.sprite.y + relative_position[1],
                batch=body.sprite.batch, group=body.window.bg_group
            )
            if not glow_color:
                glow_color = (255, 255, 255)
            self.glow.color = glow_color
            self.glow.opacity = 0
        else:
            self.glow = None

    def update_pos(self):
        self.sprite.x, self.sprite.y = rotate2d(
            -math.radians(self.body.angle + 90), (
                self.body.sprite.x + self.body_pos[0] + self.offset[0],
                self.body.sprite.y + self.body_pos[1] + self.offset[1]
            ),
            (self.body.sprite.x, self.body.sprite.y)
        )
        self.sprite.rotation = self.body.angle + 90

        if self.glow:
            self.glow.x, self.glow.y = (
                self.sprite.x, self.sprite.y
            )
            self.glow.rotation = self.body.angle + 90

    def update(self, dt):
        pass
