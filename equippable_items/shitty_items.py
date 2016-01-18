# Shitty temporary items 


class L1_Sword(Equippable):

    def __init__(self):
        super().__init__("weapon_l")
        self.name = "Shitty Sword 1"
        self.stats["dmg"] = 10
        self.modifiers["agi"] = 5


class L1_Armor(Equippable):

    def __init__(self):
        super().__init__("torso")
        self.name = "Shitty Armor 1"
        self.stats["armor"] = 5
        self.stats["hp"] = 30
        self.modifiers["str"] = 5


class L1_Helmet(Equippable):

    def __init__(self):
        super().__init__("torso")
        self.name = "Shitty Helmet 1"
        self.stats["armor"] = 3
        self.stats["hp"] = 20
        self.modifiers["str"] = 3


class L1_Ring(Equippable):

    def __init__(self):
        super().__init__("acc_1")
        self.name = "Shitty Ring 1"
        self.stats["sp"] = 5
        self.modifiers["int"] = 3
