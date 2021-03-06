import logging
import pyglet
from functions import *
from load_config import ConfigSectionMap as load_cfg
from actor import Actor
# from zsprite import ZSprite


class Enemy(Actor):

    def __init__(
        self, game, window=None, x=0, y=0,
        modifiers=None
    ):
        super().__init__()
        self.game = game
        self.x, self.y, self.z = x, y, y
        self.rectangle = create_rectangle(x, y, 32, 32)
        self.hash_position = self.game.spatial_hash.insert_object_for_point(
            (self.x, self.y), self
        )
        if window:
            logging.debug("Adding sprite to enemy.")
            self.window = window
            sx, sy = self.window.get_windowpos(x, y)
            self.sprite = pyglet.sprite.Sprite(
                window.textures["goblin"],
                x=sx, y=sy,
                batch=window.batches["creatures"],
                subpixel=True
            )
            # print(self.sprite.image.z)
        else:
            logging.info("No window specified, not adding sprite to enemy.")
        if modifiers:
            self.modifiers = modifiers
        else:
            self.modifiers = dict(
                str=5,
                int=5,
                cha=5,
                agi=5
            )

        self.base_stats = load_cfg("EnemyBaseStats")

        self.active_effects = []

        self.auto_attack_target = None
        self.attack_cd = 0

        self.hp = self.max_hp = self.base_stats["hp"]
        self.mp = self.max_mp = self.base_stats["mp"]
        self.sta = self.max_sta = self.base_stats["sta"]

        self.update_stats()
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.sta = self.max_sta

    def update_offset(self, dx=False, dy=False):
        pass

    def apply_modifier(self, mtype):
        m = self.modifiers
        bs = self.base_stats
        if mtype == "ms":
            return bs["ms"] + (m["agi"] * 3)
        elif mtype == "armor":
            return int(bs["armor"] + m["agi"] * 0.5)  # Rounds down
        elif mtype == "dmg":
            return int(bs["dmg"] + m["str"])

    def get_stat(self, stat):
        return self.base_stats[stat]

    def auto_attack(self, dt):
        t = self.auto_attack_target
        if self.attack_cd <= 0:
            if t:
                dist = get_dist(self.x, self.y, t.x, t.y)
                attack_range = self.base_stats["arng"]
                if dist <= attack_range:
                    # angle = math.degrees(
                    #     get_angle(self.x, self.y, t.x, t.y)
                    # )
                    # if (
                    #     self.angle >= angle - 45 and
                    #     self.angle <= angle + 45
                    # ):
                    self.attack(t)
                    self.attack_cd = self.base_stats["aspd"]
        else:
            self.attack_cd -= dt

    def attack(self, t):
        # attack_effects = self.attack_effects.copy()
        # attack_effects["dmg"] = self.stats.get("dmg")
        # attack_effects["crit"] = self.stats.get("crit")
        # result = t.do_effect(attack_effects)
        # self.attack_fx(t)
        # if result["crit"]:
        #     force = 100
        # else:
        t.hp -= self.base_stats["dmg"]
        force = 40
        vec = ((t.x - self.x), (t.y - self.y))
        force_x = force_y = force
        force_x -= abs(vec[0])
        force_y -= abs(vec[1])
        force_vec = (vec[0] * force_x), (vec[1] * force_y)
        t.body.apply_impulse(force_vec)

    def update_stats(self, update_ui=False):
        bs = self.base_stats
        m = self.modifiers
        self.max_hp = bs["hp"] + (m["str"] * 5)
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        self.max_mp = bs["mp"] + (m["int"] * 5)
        if self.mp > self.max_mp:
            self.mp = self.max_mp
        self.max_sta = bs["sta"] + (m["agi"] * 5)
        if self.sta > self.max_sta:
            self.sta = self.max_sta

    def critical_strike(self, critchance):
        if random.randrange(1, 100) <= critchance:
            return True
        else:
            return False

    def do_effect(self, effects, origin=None):
        # print(effects)
        if effects["dmg"]:
            crit = False
            text = str(int(effects["dmg"]))
            try:
                if self.critical_strike(effects["crit"]):
                    effects["dmg"] = int(effects["dmg"] * 1.5)
                    text = str(int(effects["dmg"])) + "!"
                    crit = True
            except KeyError:
                pass

            self.hp -= effects["dmg"]

            try:
                try:
                    if effects["dmg_type"] == "physical":
                        c = "darkred"
                    else:
                        c = "yellow"
                except KeyError:
                    c = "red"
                if crit:
                    scale = 2.0
                else:
                    scale = 1.0
                self.game.window.ui.add_combat_text(
                    text,
                    x=self.x, y=self.y + self.sprite.height,
                    scale=scale, color=c
                )
            except AttributeError as e:
                print(e)
        if effects["aoe"]:
            effects_aoe = effects.copy()
            if effects["aoe_dmg"]:
                effects_aoe["dmg"] = effects["aoe_dmg"]
            if effects["dot_dmg"]:
                effects_aoe["dot_dmg"] = effects["dot_dmg"] / 2
            effects_aoe["aoe"] = 0
            for aoe_e in self.game.enemies:
                if not aoe_e == self:
                    if check_range(
                        (self.x, self.y), (aoe_e.x, aoe_e.y),
                        effects["aoe"]
                    ):
                        aoe_e.do_effect(effects_aoe)
                        logging.debug("AOE hit target!")
        if effects["dot"]:
            effects["dot"](self, dmg=effects["dot_dmg"], origin=origin)

        if self.hp <= 0:
            if origin:
                origin.award_kill(xp=10)
            self.die()

        return dict(
            dmg=effects["dmg"],
            crit=crit
        )

    def reset(self):
        self.hp, self.mp, self.sta = self.max_hp, self.max_mp, self.max_sta

    def die(self):
        logging.info("Enemy died!")
        pos = self.window.get_windowpos(self.x, self.y, precise=True)
        self.window.animator.spawn_anim("Blood Splash", pos, scale=0.4)
        self.active_effects = []
        self.remove_body()
        if self in self.game.enemies:
            self.game.enemies.remove(self)
            self.sprite.visible = False
        if (
            self == self.game.player.target or
            self == self.game.player.auto_attack_target
        ):
            self.game.player.clear_target()

        self.game.spatial_hash.remove_object(self)

    def update(self, dt):
        if self.hp <= 0:
            self.die()
        else:
            self.update_stats()
            for e in self.active_effects:
                e.update(dt)
            self.brain.update()
            self.auto_attack(dt)
            oldx, oldy = self.x, self.y
            self.movement.update(dt)
            self.x, self.y = self.body.position
            if not (self.x == oldx) or not (self.y == oldy):
                self.game.spatial_hash.remove_object(self, self.hash_position)
                self.hash_position = self.game.spatial_hash.insert_object_for_point(
                    (self.x, self.y), self
                )
                # self.sprite._set_z(-int(self.y))
                # self.sprite._set_z(-(self.sprite.y))
                # self.sprite.z = int(self.window.height - self.sprite.y) // 8
                # newgroup = pyglet.graphics.OrderedGroup(self.hash_position[1])
                # if not self.sprite.group == newgroup:
                #     self.sprite.group = newgroup
            newpos = self.window.get_windowpos(
                self.x, self.y + self.sprite.height // 5, precise=True
            )
            self.rectangle = create_rectangle(self.x, self.y, 32, 32)
            # print(newpos)
            self.sprite.x, self.sprite.y = newpos
            #print(self.sprite.z)
