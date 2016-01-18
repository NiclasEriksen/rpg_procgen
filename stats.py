

class StatSystem:

    def __init__(self, owner):
        self.owner = owner
        self.base_stats = None
        self.base_attack = None
        self.item_bonuses = None
        self.item_bonuses_base = dict(
            str=0,
            int=0,
            agi=0,
            ms=0,
            hp=0,
            mp=0,
            sta=0,
            dmg=0,
            sp=0,
            aspd=0,
            arng=0,
            crit=0,
            hp_regen=0.,
            mp_regen=0.,
            sta_regen=0.,
            armor=0,
        )

    def get(self, name, precise=False):
        bs = self.get_all_stats()  # Fetch a new dict of base stats with
        if name == "agi" or name == "str" or name == "int":
            return bs[name]
        if name == "ms":               # item bonuses added
            if self.owner.actions["sprint"]:
                return (bs["ms"] + (bs["agi"])) * 2
            else:
                return bs["ms"] + bs["agi"]
        elif name == "armor":
            return int(bs["armor"] + bs["agi"] * 0.5)  # Rounds down
        elif name == "dmg":
            dmg = bs["dmg"] + bs[self.owner.mainstat]
            return int(dmg)
        elif name == "arng":
            return bs["arng"]
        elif name == "crit":
            return bs["crit"] + 0.2 * bs["agi"]
        elif name == "hp":
            return self.owner.hp
        elif name == "mp":
            return self.owner.mp
        elif name == "sta":
            return self.owner.sta
        elif name == "sp":
            return bs["sp"]
        elif name == "aspd":
            return bs["aspd"]
        elif name == "hp_regen":
            return round(bs["hp_regen"] + 0.1 * bs["str"], 1)
        elif name == "mp_regen":
            return round(bs["mp_regen"] + 0.2 * bs["int"], 1)
        elif name == "sta_regen":
            return round(bs["sta_regen"] + 0.3 * bs["agi"], 1)

    def apply(self, target_effects=None):
        pass

    def update_owner_stats(self):
        bs = self.get_all_stats()
        self.owner.max_hp = bs["hp"] + (bs["str"] * 5)
        if self.owner.hp > self.owner.max_hp:
            self.owner.hp = self.owner.max_hp
        self.owner.max_mp = bs["mp"] + (bs["int"] * 5)
        if self.owner.mp > self.owner.max_mp:
            self.owner.mp = self.owner.max_mp
        self.owner.max_sta = bs["sta"] + (bs["agi"] * 5)
        if self.owner.sta > self.owner.max_sta:
            self.owner.sta = self.owner.max_sta

        for key, a in self.owner.abilities.items():
            if a:
                a.update()

    def increase_stat(self, stat):
        self.base_stats[stat] += 1

    def recalculate_items(self):
        ib = self.item_bonuses_base.copy()
        for slot, item in self.owner.equipped_items.items():
            if item:
                for stat, value in item.get_stats().items():
                    ib[stat] += value
        self.item_bonuses = ib

    def get_all_stats(self):
        bs = self.base_stats.copy()
        for key, value in self.item_bonuses.items():
            bs[key] += value
        return bs

    def set_base_stats(self, base_stats):
        self.base_stats = base_stats

    def set_base_attack(self, base_attack):
        self.base_attack = base_attack
