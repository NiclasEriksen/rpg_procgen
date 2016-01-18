# Spells and abilities
import pyglet
import logging
import math
import os
import glob
# from main import logging, pyglet
from functions import *
from enemy import Enemy
from dungeon_generator import Wall, Collidable
ROOT = os.path.dirname(__file__)
ABILITY_PATH = os.path.join(ROOT, "ability_files/")


class UsableAbility:

    """Constructor for player abilities."""

    def __init__(self):
        self.owner = None
        self.range = 0
        self.target = None
        self.cooldown_timer = 0
        self.ability_attr = dict(
            lvl=0,
            max_lvl=99,
            name="",
            type=None,
            magic_type=None,
            cost=0,
            cost_type=None,
            range=0,
            hit_range=0,
            speed=0,
            cast_time=0,
            move_interrupt=False,
            penetration=False,
            cooldown=0
        )
        self.target_effects_base = dict(
            dmg=0,
            dmg_type="physical",
            heal=0,
            stun=0,
            slow=0,
            aoe=0,
            aoe_dmg=0,
            dot=None,
            dot_dmg=None,
            hot=None,
            hot_dmg=None,
            penetration=0,
            crit=0
        )

    def get_cost(self, type=None):
        if type:
            pass
        else:
            pass

    def get_name(self):
        if self.ability_attr["name"]:
            return "{0} lvl. {1}".format(
                self.ability_attr["name"],
                self.ability_attr["lvl"]
            )
        else:
            return "UNKNOWN"

    def get_effect_list(self):
        """Returns a list of effects the ability has in formatted strings."""
        list = []
        for e, val in self.target_effects.items():
            if val:
                list.append(
                    "{0}: {1}".format(
                        translate_stat(e), val
                    )
                )
        return list

    def levelup(self, lvl=False):
        """Level up ability, optional argument defines what level."""
        if lvl and lvl <= self.ability_attr["max_lvl"] and lvl > 0:
            self.ability_attr["lvl"] = lvl
        elif self.ability_attr["lvl"] < self.ability_attr["max_lvl"]:
            self.ability_attr["lvl"] += 1
        else:
            logging.info("Skill is at its max level already.")

        self.apply_level_scaling()

    def apply_level_scaling(self):
        lvl = self.ability_attr["lvl"]
        if hasattr(self, "level_scale_attr"):
            for key, value in self.level_scale_attr.items():
                try:
                    self.ability_attr[key] = value[lvl - 1]
                except IndexError:
                    logging.warning("Ability has no value for that lvl.")
        if hasattr(self, "level_scale_effect"):
            print("YOOOHO")

    def apply_modifiers(self):
        if self.owner:
            self.target_effects = self.target_effects_base.copy()
            if self.ability_attr["type"] == "spell":
                sp = self.owner.stats.get("sp")
                self.target_effects["dmg"] += sp
                if self.target_effects["dot_dmg"]:
                    self.target_effects["dot_dmg"] += sp * 2
            crit = self.owner.attack_effects["crit"]
            self.target_effects["crit"] += crit

    def update(self):
        self.apply_modifiers()

    def do_cost(self, dry=False):
        if self.ability_attr["cost_type"] == "mp":
            if self.owner.mp >= self.ability_attr["cost"]:
                if not dry:
                    self.owner.mp -= self.ability_attr["cost"]
                return True
            else:
                logging.info("Not enough mana for that ability.")
                return False
        elif self.ability_attr["cost_type"] == "sta":
            if self.owner.sta >= self.ability_attr["cost"]:
                if not dry:
                    self.owner.sta -= self.ability_attr["cost"]
                return True
            else:
                logging.info("Not enough stamina for that ability.")
                return False

    def use(self, target=None):
        success = False
        if not self.owner.cast_object:
            if self.ability_attr["cast_time"]:
                if self.do_cost(dry=True):
                    self.owner.halt_movement()
                    self.target = target
                    self.owner.cast_object = Cast(self)
                    success = True
            else:
                self.target = target
                success = self.cast()
        else:
            logging.info("Player is busy casting another ability.")

        return success

    def cast(self):
        success = False
        self.owner.cast_object = None
        if hasattr(self, "custom_action"):
            self.custom_action(self.target)
            success = True
        elif isinstance(self, ProjectileAbility):
            if self.target:
                if self.do_cost():
                    if isinstance(self, MultiProjectileAbility):
                        self.fire_multiple(self.target)
                    else:
                        p1 = (self.owner.x, self.owner.y)
                        p2 = self.target
                        angle = get_angle(*p1, *p2)
                        self.fire(angle)
                    success = True
            else:
                logging.debug("No target for projectile, aborting.")

        return success


class Cast:

    def __init__(self, ability):
        self.ability = ability
        self.time = ability.ability_attr["cast_time"]
        self.timer = 0

    def update(self, dt):
        # self.ability.target = self.ability.owner.window.get_windowpos(
        #     *self.ability.target
        # )
        self.timer += dt
        if self.timer >= self.time:
            self.ability.cast()


class SingleTargetAbility(UsableAbility):

    """Constructor for abilities that require a target."""

    def __init__(self):
        super().__init__()


class ProjectileAbility(UsableAbility):

    """Constructor for projectile based abilities"""

    def __init__(self):
        super().__init__()

    def fire(self, angle):
        try:
            o = self.owner
            # logging.debug("Firing a projectile at {0}".format(target))
            p = Projectile(
                (o.x, o.y), angle,
                self.ability_attr,
                self.target_effects, o, self.projectile_tex
            )
            if hasattr(self, "impact_anim"):
                p.impact_anim = self.impact_anim
            if hasattr(self, "impact_anim_scale"):
                p.impact_anim_scale = self.impact_anim_scale
            if hasattr(self, "projectile_anim"):
                p.projectile_anim = self.projectile_anim
            if hasattr(self, "projectile_anim_scale"):
                p.projectile_anim_scale = self.projectile_anim_scale
            p.do_fire_anim()
            o.child_objects.append(p)
        except AttributeError as e:
            logging.error(e)


class MultiProjectileAbility(ProjectileAbility):

    """Constructor for projectile based abilities with multiple projectiles"""

    def __init__(self):
        super().__init__()

    def fire_multiple(self, target):
        p1 = (self.owner.x, self.owner.y)
        p2 = target
        mid_angle = math.degrees(get_angle(*p1, *p2))
        begin_spread = -self.spread
        for i in range(self.projectile_count):
            angle = math.radians(mid_angle + begin_spread + self.spread * i)
            self.fire(angle)


class Projectile:

    def __init__(
        self, source, angle, attributes, effects, owner, texture
    ):
        (self.x, self.y) = source
        self.speed = attributes["speed"]
        self.range = attributes["range"]
        self.penetration = attributes["penetration"]
        self.blacklist = []
        self.distance_travelled = 0
        self.target_effects = effects
        self.owner = owner
        self.game = owner.game
        self.sprite = None
        self.anim = None
        self.angle = angle
        if self.game.window:  # Projectile needs window to get real position
            self.window = self.game.window
            p1 = source
            x, y = self.window.get_windowpos(*p1, precise=True)
            if texture:
                self.sprite = pyglet.sprite.Sprite(
                    texture,
                    x=x, y=y,
                    batch=self.window.batches["projectiles"],
                    subpixel=True,
                )
                # self.sprite.image.anchor_y = 0
                if hasattr(texture, "scale"):
                    self.sprite.scale = texture.scale
                self.sprite.rotation = math.degrees(angle)
        else:
            self.window = None

    def do_fire_anim(self):
        if hasattr(self, "projectile_anim"):
            self.sprite.batch = None
            pos = self.window.get_windowpos(self.x, self.y, precise=True)
            self.anim = self.owner.window.get_anim(self.projectile_anim)
            self.anim.owner = self
            self.anim.animator.set_anchor(self.anim._animation, y=-12)
            self.anim.animator.set_duration(
                self.anim._animation, 1.0 / (self.speed // 10)
            )
            self.anim.rotation = math.degrees(self.angle) - 90
            self.anim.position = pos
            if hasattr(self, "projectile_anim_scale"):
                self.anim.scale = self.projectile_anim_scale
            else:
                self.anim.scale = 1.0

    def check_hit(self):
        enemies = self.game.spatial_hash.get_objects_from_point(
            (self.x, self.y), radius=32, type=Enemy
        )
        for e in enemies:
            if e not in self.blacklist:
                if check_point_rectangle(self.x, self.y, e.rectangle):
                    e.do_effect(self.target_effects)
                    if hasattr(self, "impact_anim"):
                        pos = self.owner.window.get_windowpos(
                            self.x, self.y, precise=True
                        )
                        if hasattr(self, "impact_anim_scale"):
                            scale = self.impact_anim_scale
                        else:
                            scale = 1.0
                        self.owner.window.animator.spawn_anim(
                            self.impact_anim, pos, scale=scale,
                            rotation=math.degrees(self.angle)
                        )
                    logging.debug("Projectile hit target!")
                    if self.penetration > 0:
                        if e.hp > 0:
                            self.blacklist.append(e)
                    return True
        walls = self.game.spatial_hash.get_objects_from_point(
            (self.x, self.y), type=Collidable
        )
        for w in walls:
            r = create_rect(*w.p1, 32, 32)
            if check_point_rectangle(self.x, self.y, r):
                self.penetration = 0
                return True
        else:
            return False

    def update(self, dt):
        if self.check_hit():
            if self.penetration <= 0:
                self.blacklist = []
                self.owner.child_objects.remove(self)
            else:
                self.penetration -= 1
        elif self.distance_travelled >= self.range:
            self.blacklist = []
            self.owner.child_objects.remove(self)
        else:
            r = self.speed * dt
            self.distance_travelled += r
            self.x += r*math.cos(self.angle)
            self.y -= r*math.sin(self.angle)
            if self.sprite and self.window:
                x, y = self.window.get_windowpos(self.x, self.y, precise=True)
                self.sprite.x = x
                self.sprite.y = y
            if self.anim and self.window:
                x, y = self.window.get_windowpos(self.x, self.y, precise=True)
                self.anim.position = (x, y)
                self.anim.draw()
            if not self.anim and not self.sprite.batch:
                self.sprite.batch = self.window.batches["projectiles"]


class DoT:

    """Constructor for DoT (damage over time) objects"""

    def __init__(self, owner, dmg, time, tick, atype="spell", dtype="none"):
        self.owner = owner
        self.tick = tick
        self.ability_type = atype
        self.target_effects = dict(
            dmg=dmg,
            dmg_type=dtype,
            stun=0,
            slow=0,
            aoe=0,
            aoe_dmg=0,
            dot=None,
        )
        self.time = tick
        self.ticks = int(time / tick)
        tick_dmg = self.target_effects["dmg"] / self.ticks
        self.target_effects["dmg"] = tick_dmg

    def do_effect(self):
        self.owner.do_effect(self.target_effects)
        if hasattr(self, "tick_effect"):
            if hasattr(self, "tick_effect_scale"):
                scale = self.tick_effect_scale
            else:
                scale = 1.0
            pos = self.owner.window.get_windowpos(
                self.owner.x, self.owner.y, precise=True
            )
            self.owner.window.animator.spawn_anim(
                self.tick_effect, pos, scale=scale
            )

    def update(self, dt):
        if self.ticks:
            if self.time > 0:
                self.time -= dt
            else:
                # Adds current time to timer in case it's negative
                self.time = self.tick + self.time
                self.ticks -= 1
                self.do_effect()
        else:
            self.owner.active_effects.remove(self)


# Reads all python files in the ability directory and executes them,
# adding the abilities to the game
for ability_file in glob.glob(ABILITY_PATH + '*.py'):
    exec(open(ability_file).read(), globals())
