import pyglet.sprite


class Batch(object):
    def __init__(self, batchname):
        self.batch = batchname


class Attributes(object):
    def __init__(self):
        self.point = {
            "str": 0,
            "agi": 0,
            "int": 0
        }
        self.updated = False


class EffectiveStats(object):
    def __init__(self):
        self.type = {
            "hp_max": 0,
            "sta_max": 0,
            "mana_max": 0,
            "armor": 0,
            "magic_def": 0,
            "ms": 0,
            "dmg": 0,
            "aspd": 0,
            "arng": 0,
            "crit_chance": 0,
            "crit_power": 0,
            "armor_pen": 0,
            "sp": 0,
            "sp_crit_chance": 0,
            "sp_crit_power": 0,
            "sp_pen": 0
        }
        self.initialized = False


class BaseStats(object):
    def __init__(self):
        self.type = {
            "hp_max": 10,
            "sta_max": 10,
            "mana_max": 10,
            "armor": 0,
            "magic_def": 0,
            "ms": 80,
            "dmg": 1,
            "aspd": 30,
            "arng": 40,
            "crit_chance": 0,
            "crit_power": 0,
            "armor_pen": 0,
            "sp": 0,
            "sp_crit_chance": 0,
            "sp_crit_power": 0,
            "sp_pen": 0
        }


class ActiveAbilities(object):
    def __init__(self):
        self.slots = {
            1: None, 2: None,
            3: None, 4: None,
            5: None, 6: None,
            7: None, 8: None,
            9: None, 10: None,
            11: None, 12: None,
            13: None, 14: None,
            15: None, 16: None
        }


class PassiveAbilities(object):
    def __init__(self):
        self.slots = {
            1: None, 2: None,
            3: None, 4: None,
            5: None, 6: None,
            7: None, 8: None,
            9: None, 10: None,
            11: None, 12: None,
            13: None, 14: None,
            15: None, 16: None
        }


class Equipment(object):
    def __init__(self):
        self.slots = {
            "head": None,
            "neck": None,
            "torso": None,
            "shoulders": None,
            "wrists": None,
            "hands": None,
            "legs": None,
            "feet": None,
            "ring1": None,
            "ring2": None,
            "trinket1": None,
            "trinket2": None,
            "mainhand": None,
            "offhand": None
        }
        self.changed = False


class ActiveEffects(object):
    def __init__(self):
        self.buffs = []
        self.debuffs = []


class XP(object):
    def __init__(self):
        self.count = 0
        self.rate = 1


class Level(object):
    def __init__(self):
        self.lvl = 1
        self.lvlup_xp = 30


class IsPlayer(object):
    def __init__(self):
        pass


class IsMob(object):
    def __init__(self):
        pass


class Input(object):
    def __init__(self):
        pass


class KeyboardControl(object):
    def __init__(self):
        pass


class Movement(object):
    def __init__(self):
        self.max_speed = 120
        self.acceleration = self.max_speed / 15


class StaticPosition(object):
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y


class CharName(object):
    def __init__(self, name=None):
        self.name = name


class Position(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.old_x, self.old_y = x, y

    def set(self, x, y):
        self.old_x, self.old_y = self.x, self.y
        self.x, self.y = x, y


class WindowPosition(object):
    def __init__(self, x=0, y=0, static=False):
        self.x = x
        self.y = y
        self.static = static


class Velocity(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Sprite(object):
    def __init__(self, img):
        self.sprite = pyglet.sprite.Sprite(img, subpixel=True)
        self.batchless = False


class PhysBody(object):
    def __init__(self, mass=10, width=24, height=24, shape="circle"):
        self.body = None
        self.mass = mass
        self.width = width
        self.height = height
        self.shape = shape


class HP(object):
    def __init__(self, amount=1):
        self.value = amount
        self.max = amount


class Stamina(object):
    def __init__(self, amount=1):
        self.value = amount
        self.max = amount


class Mana(object):
    def __init__(self, amount=1):
        self.value = amount
        self.max = amount


class LastAttacker(object):
    def __init__(self):
        self.who = None


class AutoAttackTarget(object):
    def __init__(self):
        self.who = None


class FocusTarget(object):
    def __init__(self):
        self.who = None


class TargetEffects(object):
    def __init__(self):
        pass


class EffectTarget(object):
    def __init__(self):
        pass


class BasicAttack(object):
    def __init__(self):
        self.dmg = 1
        self.effects = None
