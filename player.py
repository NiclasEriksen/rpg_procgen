import random
import pyglet
import logging
import os
import glob
import math
from functions import *
from actor import Actor, Hand
from stats import StatSystem
from animations import HandAnimAttack, HeadBobbing, Pulse
from load_config import ConfigSectionMap as load_cfg
import abilities
ROOT = os.path.dirname(__file__)
CLASSES_PATH = os.path.join(ROOT, "classes/")


class Player(Actor):

    def __init__(
        self, game, window=None, x=0, y=0,
        modifiers={'str': 5, 'int': 5, 'cha': 5, 'agi': 5}, mainstat="agi"
    ):
        super().__init__()
        self.game = game
        self.child_objects = []
        self.cast_object = None
        self.x, self.y = x, y
        self.lhand_offset = (0, 0)
        self.rhand_offset = (0, 0)
        self.body_offset = (0, 0)
        self.child_objects.append(HeadBobbing(self, duration=0.5, amount=3))
        if window:
            self.windowpos = (window.width // 2, window.height // 2)
            logging.debug("Adding sprite to player.")
            self.window = window
            sprite_x, sprite_y = window.get_windowpos(x, y, precise=True)
            self.sprite = pyglet.sprite.Sprite(
                window.textures["player_body"],
                x=window.width // 2, y=window.height // 2,
                batch=window.batches["creatures"], group=window.fg_group
            )
            self.glow = pyglet.sprite.Sprite(
                window.textures["player_body_glow"],
                x=window.width // 2, y=window.height // 2,
                batch=window.batches["creatures"], group=window.mid_group
            )
            self.glow.color = (255, 255, 255)
            self.glow.opacity = 0
        else:
            logging.info("No window specified, not adding sprite to player.")

        self.limbs = dict(
            left=Hand(
                self, (-10, 8), window.textures["player_hand"],
                glow_texture=window.textures["player_hand_glow"],
                glow_color=(20, 160, 120)
            ),
            right=Hand(
                self, (10, 8), window.textures["player_hand"],
                glow_texture=window.textures["player_hand_glow"],
                glow_color=(175, 50, 110)
            )
        )
        self.child_objects.append(Pulse(self.limbs["right"].glow))
        self.child_objects.append(
            Pulse(self.limbs["left"].glow, frequency=0.3)
        )
        self.child_objects.append(
            Pulse(
                self.glow, frequency=2.5,
                max_opacity=0.3, min_scale=0.8, max_scale=1.3
            )
        )

        self.action = None
        self.actions = dict(
            sprint=False,
            movement=False,
            targeting=False,
        )
        self.auto_attack_target = None
        self.target = None
        self.modifiers = modifiers
        self.modifiers_items = modifiers
        self.mainstat = mainstat
        self.move_dir = dict(
            left=False,
            right=False,
            up=False,
            down=False
        )
        self.last_dir = "down"
        self.head_dir = (1, 0)

        self.base_stats = load_cfg("PlayerBaseStats")
        self.base_stats_items = self.base_stats.copy()

        self.equipped_items = dict(
            head=None,
            torso=None,
            hands=None,
            feet=None,
            acc_1=None,
            acc_2=None,
            weapon_l=None,
            weapon_r=None,
            weapon_2h=None
        )

        self.attack_effects = dict(
            dmg=30,
            dmg_type="physical",
            stun=0,
            slow=0,
            aoe=0,
            aoe_dmg=0,
            dot=None,
            dot_dmg=None,
            penetration=0,
            crit=10
        )

        self.stats = StatSystem(self)
        self.stats.set_base_attack(self.attack_effects)
        self.stats.set_base_stats(self.base_stats)
        self.stats.recalculate_items()

        self.abilities = dict(
            slot1=abilities.FireBall(self),
            slot2=abilities.SpreadBalls(self),
            slot3=abilities.Blink(self),
            slot4=abilities.Spark(self),
        )

        self.hp = self.max_hp = self.base_stats["hp"]
        self.mp = self.max_mp = self.base_stats["mp"]
        self.sta = self.max_sta = self.base_stats["sta"]
        self.xp = 0
        self.attack_cd = 0

        self.update_stats()
        self.restore_stats()

    def get_windowpos(self):
        return self.windowpos

    def award_kill(self, xp=0, gold=0):
        if xp:
            self.xp += xp
            print(self.xp)
        if gold:
            pass

    def levelup(self, attribute=None):
        if not attribute:   # If no attribute given, assign random upgrade
            attribute = random.choice(["str", "int", "agi"])

        # Increases the chosen attribute by 1
        self.stats.increase_stat(attribute)
        logging.info(
            "Level up, increased attribute \"{0}\" by 1 to {1}".format(
                attribute, self.stats.get(attribute)
            )
        )
        self.update_stats()
        self.restore_stats()

    def restore_stats(self):
        logging.debug("Player hp, mana and stamina restored to full status.")
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.sta = self.max_sta

    def equip_item(self, item):
        if not self.equipped_items[item.slot]:
            self.equipped_items[item.slot] = item
            logging.debug(
                "Player equipped item {0} in slot {1}.".format(
                    item.get_name(), item.slot
                )
            )

        self.stats.recalculate_items()

    def unequip_item(self, slot):
        if self.equipped_items[slot]:
            logging.info(
                "Removed item {0} in slot {1} from player".format(
                    self.equipped_items[slot], slot
                )
            )
            self.equipped_items[slot] = None
        else:
            logging.error("No item in slot \"{0}\"".format(slot))

        self.stats.recalculate_items()

    def use_ability(self, ability, target=None):
        a = None
        if ability == 1:
            a = self.abilities["slot1"]
        elif ability == 2:
            a = self.abilities["slot2"]
        elif ability == 3:
            a = self.abilities["slot3"]
        elif ability == 4:
            a = self.abilities["slot4"]

        if a:
            logging.debug("Player uses ability {}.".format(a.get_name()))
            if isinstance(a, abilities.ProjectileAbility):
                self.window.set_reticule("projectile")
                self.actions["targeting"] = a
            else:
                self.clear_ability_target()
                a.use(target=target)
        else:
            logging.debug("No ability in slot {0}.".format(ability))

    def clear_ability_target(self):
        self.actions["targeting"] = False
        self.window.set_reticule("default")

    def set_target(self, target):
        self.target = target

    def clear_target(self):
        self.auto_attack_target = None
        self.target = None

    def move(self, dt, newpos=False):
        old_x, old_y = self.x, self.y
        if newpos:
            x, y = newpos
        else:
            x, y = old_x, old_y
            d = self.move_dir
            ms = self.stats.get("ms")
            if ms > self.max_velocity:
                ms = self.max_velocity

            for key, value in d.items():
                if value:
                    self.actions["movement"] = True
                    break
            else:
                self.actions["movement"] = False

            if (d["up"] or d["down"]) and not (d["up"] == d["down"]):
                if (d["left"] or d["right"]) and not (d["left"] == d["right"]):
                    ms /= get_diag_ratio()  # Reduces movement speed if diag

            if d["up"] and not d["down"]:
                if self.body.velocity.y < ms:
                    self.body.velocity.y += ms * 5 * dt
                y += dt * ms
            if d["down"] and not d["up"]:
                y -= dt * ms
                if self.body.velocity.y > -ms:
                    self.body.velocity.y -= ms * 5 * dt
            if d["left"] and not d["right"]:
                if self.body.velocity.x > -ms:
                    self.body.velocity.x -= ms * 5 * dt
                # x -= dt * ms
            if d["right"] and not d["left"]:
                if self.body.velocity.x < ms:
                    self.body.velocity.x += ms * 5 * dt

        self.x, self.y = self.body.position
        if newpos:
            self.x, self.y = x, y
            self.body.position = x, y
        self.window.update_offset(dx=old_x - self.x, dy=old_y - self.y)

    def halt_movement(self):
        for key, value in self.move_dir.items():
            self.move_dir[key] = False

    def set_move_sprite(self):
        anim = self.window.player_anim_grid
        static = self.window.player_static_img
        d = self.move_dir
        spd = 0.2 * 80 / self.stats.get("ms")
        if d["left"] and d["down"]:
            self.last_dir = "leftdown"
            if not self.sprite.image == anim["leftdown"]:
                self.sprite.image = anim["leftdown"]
        elif d["right"] and d["down"]:
            self.last_dir = "rightdown"
            if not self.sprite.image == anim["rightdown"]:
                self.sprite.image = anim["rightdown"]
        elif d["left"] and d["up"]:
            self.last_dir = "leftup"
            if not self.sprite.image == anim["leftup"]:
                self.sprite.image = anim["leftup"]
        elif d["right"] and d["up"]:
            self.last_dir = "rightup"
            if not self.sprite.image == anim["rightup"]:
                self.sprite.image = anim["rightup"]
        elif d["up"] and not d["down"]:
            self.last_dir = "up"
            if not self.sprite.image == anim["up"]:
                self.sprite.image = anim["up"]
        elif d["down"] and not d["up"]:
            self.last_dir = "down"
            if not self.sprite.image == anim["down"]:
                self.sprite.image = anim["down"]
        elif d["left"] and not d["right"]:
            self.last_dir = "left"
            if not self.sprite.image == anim["left"]:
                self.sprite.image = anim["left"]
        elif d["right"] and not d["left"]:
            self.last_dir = "right"
            if not self.sprite.image == anim["right"]:
                self.sprite.image = anim["right"]
        else:
            if not self.sprite.image == static[self.last_dir]:
                self.sprite.image = static[self.last_dir]

        if isinstance(self.sprite.image, pyglet.image.Animation):
            set_duration(self.sprite.image, spd)

    def auto_attack(self, dt):
        t = self.auto_attack_target
        if t not in self.game.enemies:  # To prevent having a zombie of target
            t = self.auto_attack_target = None
        if not self.cast_object and self.attack_cd <= 0:
            if t:
                dist = get_dist(self.x, self.y, t.x, t.y)
                attack_range = self.stats.get("arng")
                if dist <= attack_range:
                    angle = math.degrees(
                        get_angle(self.x, self.y, t.x, t.y)
                    )
                    anglediff = (
                        (self.angle - angle + 180) % 360 - 180
                    )
                    if anglediff <= 45 and anglediff >= -45:
                        self.attack(t)
                        self.attack_cd = self.stats.get("aspd")
        else:
            self.attack_cd -= dt

    def attack(self, t):
        attack_effects = self.attack_effects.copy()
        attack_effects["dmg"] = self.stats.get("dmg")
        attack_effects["crit"] = self.stats.get("crit")
        result = t.do_effect(attack_effects, origin=self)
        self.attack_fx(t)
        if result["crit"]:
            force = 100
        else:
            force = 50
        vec = ((t.x - self.x), (t.y - self.y))
        force_x = force_y = force
        force_x -= abs(vec[0])
        force_y -= abs(vec[1])
        force_vec = (vec[0] * force_x), (vec[1] * force_y)
        t.body.apply_impulse(force_vec)
        if result["crit"]:
            self.child_objects.append(
                HandAnimAttack(
                    self, "left", duration=self.stats.get("aspd") / 3
                )
            )
            self.child_objects.append(
                HandAnimAttack(
                    self, "right", duration=self.stats.get("aspd") / 3
                )
            )
        else:
            hand = random.choice(["right", "left"])
            self.child_objects.append(
                HandAnimAttack(self, hand, duration=self.stats.get("aspd") / 3)
            )

    def critical_strike(self, critchance):
        if random.randrange(1, 100) <= critchance:
            return True
        else:
            return False

    def attack_fx(self, t):
        midpoint = get_midpoint((self.x, self.y), (t.x, t.y))
        fx_point = get_midpoint(midpoint, (t.x, t.y))
        apos = self.game.window.get_windowpos(
            *fx_point
        )
        effect = random.choice(["Melee 1", "Melee 2", "Melee 5"])
        self.game.window.animator.spawn_anim(
            effect, apos, scale=0.25,
            rotation=self.angle - 45
        )

    def update_stats(self):
        self.stats.update_owner_stats()

    def update_regen(self, dt):
        if self.hp < self.max_hp:
            self.hp += self.stats.get("hp_regen") * dt
        if self.mp < self.max_mp:
            self.mp += self.stats.get("mp_regen") * dt
        if self.sta < self.max_sta and not self.actions["sprint"]:
            self.sta += self.stats.get("sta_regen") * dt

    def update_degen(self, dt):
        if self.actions["sprint"]:
            if self.sta > 0:
                for d, val in self.move_dir.items():
                    if val:
                        self.sta -= 15 * dt
                        break
            else:
                self.actions["sprint"] = False

    def update_body(self):
        angle = get_angle(self.sprite.x, self.sprite.y, *self.window.mouse_pos)
        self.angle = math.degrees(angle)
        for key, limb in self.limbs.items():
            limb.update_pos()

        # self.rhand_sprite.x, self.rhand_sprite.y = rotate2d(
        #     -angle, (
        #         self.sprite.x + 8 + self.rhand_offset[1],
        #         self.sprite.y - 12 + self.rhand_offset[0]
        #     ),
        #     (self.sprite.x, self.sprite.y)
        # )
        # self.rhand_glow.x, self.rhand_glow.y = (
        #     self.rhand_sprite.x, self.rhand_sprite.y
        # )
        # self.rhand_sprite.rotation = self.angle + 90
        # self.rhand_glow.rotation = self.angle + 90
        self.sprite.x, self.sprite.y = rotate2d(
            math.radians(self.angle + 90), (
                self.windowpos[0] + self.body_offset[0],
                self.windowpos[1] + self.body_offset[1]
            ),
            self.windowpos
        )
        self.sprite.rotation = self.angle + 90
        self.glow.x, self.glow.y = self.sprite.x, self.sprite.y
        self.glow.rotation = self.sprite.rotation

    def die(self):
        pos = self.window.get_windowpos(self.x, self.y, precise=True)
        self.window.animator.spawn_anim("Blood Splash", pos, scale=0.8)
        # self.active_effects = []
        self.limbs = {}
        self.child_objects = []
        self.sprite.delete()
        self.glow.delete()
        self.remove_body()
        self.clear_target()
        self.clear_ability_target()
        self.game.player = None
        # self.sprite.visible = False
        logging.info("Player died!")

    def update(self, dt):
        if self.hp <= 0:
            self.die()
        else:
            if self.xp >= 30:
                self.levelup()
                self.xp = 0
            self.move(dt)
            if self.actions["movement"] and self.cast_object:
                self.cast_object = None
                logging.info("Cast interrupted by movement.")
            self.auto_attack(dt)
            self.update_regen(dt)
            self.update_degen(dt)
            self.update_stats()
            for o in self.child_objects:
                try:
                    o.update(dt)
                except Exception as e:
                    logging.error(e)
            if self.cast_object:
                self.cast_object.update(dt)

            self.update_body()


class Damage:

    def __init__(self, owner, target, dmg=0, dmg_type="normal"):
        self.owner, self.target = owner, target

        if self.owner.critical_strike(self.stats.get("crit")):
            dmg = int(dmg * 1.5)
            logging.info("Critical strike!")

        self.target.hp -= dmg
        if self.target.hp < 0:
            self.target.hp = 0
        logging.debug("Target takes {0} damage.".format(dmg))

    def update(self, dt):
        pass

# Reads all python files in the classes directory and executes them,
# adding the classes to the game
for class_file in glob.glob(CLASSES_PATH + '*.py'):
    exec(open(class_file).read(), globals())
