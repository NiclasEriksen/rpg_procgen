# Items and objects
import logging
import os
import glob
# from main import logging, pyglet
ROOT = os.path.dirname(__file__)
ITEM_PATH = os.path.join(ROOT, "equippable_items/")


class Equippable:

    """Constructor for equippable items"""

    def __init__(self, slot):
        self.slot = slot
        self.stats = dict(
            ms=0,
            hp=0,
            mp=0,
            sta=0,
            dmg=0,
            sp=0,
            aspd=0,
            arng=0,
            crit=0,
            hp_regen=0,
            mp_regen=0,
            sta_regen=0,
            armor=0,
        )
        self.modifiers = dict(
            str=0,
            int=0,
            cha=0,
            agi=0
        )

    def get_stat(self, stat):
        if stat in self.stats:
            return self.stats[stat]

    def get_name(self):
        try:
            return self.name
        except AttributeError:
            logging.error("Item has no name, giving it a generic one.")
            return "UNKNOWN"

    def get_stats(self, stat=None):
        try:
            if stat:
                return self.stats[stat]
            else:
                return self.stats
        except NameError:
            logging.error("Item do no contain a list of stats, aborting")
            return False

    def get_modifiers(self, modifier=None):
        try:
            if modifier:
                return self.modifiers[modifier]
            else:
                return self.modifiers
        except NameError:
            logging.error("Item do not contain a list of modifiers, aborting")
            return False

# Reads all python files in the items directory and executes them,
# adding the items to the game
for item_file in glob.glob(ITEM_PATH + '*.py'):
    exec(open(item_file).read(), globals())
