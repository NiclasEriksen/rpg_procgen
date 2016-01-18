import glob
import logging
import pyglet
from functions import *
from pyglet.image import Animation, AnimationFrame

ANIM_PATH = "resources/animations/"


def create_effect_animation(image_name):
    img = pyglet.image.load(image_name)
    columns = img.width // 192
    rows = img.height // 192
    effect_seq = pyglet.image.ImageGrid(
        img, rows, columns
    ).get_texture_sequence()
    effect_frames = []

    for row in range(rows, 0, -1):
        end = row * columns
        start = end - (columns - 1) - 1
        for effect_frame in effect_seq[start:end:1]:
            effect_frame = center_image(effect_frame)
            effect_frames.append(AnimationFrame(effect_frame, 1 / 60))

    effect_frames[(rows * columns) - 1].duration = None

    return Animation(effect_frames)


class Animator:

    def __init__(self, window):
        self.window = window
        self.animations = dict()
        self.loaded_anims = []
        for effect_file in glob.glob(ANIM_PATH + '*.png'):
            key = effect_file[len(ANIM_PATH):-4]
            self.animations[key] = create_effect_animation(effect_file)

    def spawn_anim(self, animname, pos, scale=1.0, rotation=0):
        try:
            a = EffectSprite(self.animations[animname])
        except KeyError as e:
            logging.error("No animation by that name found: {}".format(e))
        else:
            a.animator = self
            a.game_pos = self.window.get_gamepos(*pos)
            a.position = pos
            a.scale = scale
            a.rotation = rotation
            self.loaded_anims.append(a)

    def get_anim(self, animname):
        try:
            a = EffectSprite(self.animations[animname])
        except KeyError as e:
            logging.error("No animation by that name found: {}".format(e))
        else:
            a.animator = self
            return a

    def set_duration(self, anim, duration):
        if isinstance(anim, pyglet.image.Animation):
            for f in anim.frames:
                f.duration = duration

    def set_anchor(self, anim, x="no", y="no"):
        if isinstance(anim, pyglet.image.Animation):
            for f in anim.frames:
                if type(x) is not str:
                    f.image.anchor_x = x
                if type(y) is not str:
                    f.image.anchor_y = y

    def render(self):
        for a in self.loaded_anims:
            a.position = self.window.get_windowpos(*a.game_pos, precise=True)
            a.draw()


class EffectSprite(pyglet.sprite.Sprite):

    def on_animation_end(self):
        try:
            self.animator.loaded_anims.remove(self)
        except ValueError:
            if hasattr(self, "owner"):
                self.owner.anim = False
        self.delete()


class HandAnimAttack:

    def __init__(self, owner, hand, duration=0.5, reach=12):
        self.max_offset = reach
        self.owner = owner
        self.hand = hand
        self.cur_time = 0
        self.max_time = duration

    def update(self, dt):
        if self.cur_time < self.max_time:
            offset_y = self.max_offset * smooth_in_out(
                self.cur_time / self.max_time * 1
            )
            offset_x = self.max_offset // 3 * smooth_in_out(
                self.cur_time / self.max_time * 1
            )
            if self.hand == "left":
                self.owner.lhand_offset = (-offset_x, offset_y)
            elif self.hand == "right":
                self.owner.rhand_offset = (offset_x, offset_y)
            self.cur_time += dt
        else:
            if self.hand == "left":
                self.owner.lhand_offset = (0, 0)
            elif self.hand == "right":
                self.owner.rhand_offset = (0, 0)

            self.owner.child_objects.remove(self)


class HeadBobbing:

    def __init__(self, owner, duration=0.5, amount=6):
        self.max_offset = amount
        self.owner = owner
        self.cur_time = 0
        self.max_time = duration
        self.settle = False

    def update(self, dt):
        v = abs(self.owner.body.velocity.x) + abs(self.owner.body.velocity.y)
        # self.max_time = self.owner.stats.get("ms") / 300
        if v >= 30:
            self.settle = False
        else:
            self.settle = True
        if self.cur_time < self.max_time and not self.settle:
            offset_y = self.max_offset * smooth_in_out(
                self.cur_time / self.max_time * 1
            )
            self.owner.body_offset = (0, offset_y)
            self.cur_time += dt
        else:
            if self.settle:
                if self.owner.body_offset[1] > 0:
                    self.owner.body_offset = (
                        self.owner.body_offset[0],
                        self.owner.body_offset[1] - self.max_offset * dt * 2
                    )
                else:
                    self.owner.body_offset = (0, 0)
            else:
                self.cur_time = 0
        # else:
        #     self.owner.body_offset = (0, 0)

            # self.owner.child_objects.remove(self)
