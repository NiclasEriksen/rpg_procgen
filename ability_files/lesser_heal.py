

class LesserHeal(SingleTargetAbility):

    """Simple fireball with aoe effect."""

    def __init__(self, owner):
        super().__init__()
        self.owner = owner

        self.ability_attr["lvl"] = 1
        self.ability_attr["name"] = "Lesser Heal"
        self.ability_attr["type"] = "spell"
        self.ability_attr["magic_type"] = "holy"
        self.ability_attr["cost_type"] = "mp"
        self.ability_attr["cost"] = 5
        self.ability_attr["range"] = 400
        self.ability_attr["cast_time"] = 1.0
        self.ability_attr["move_interrupt"] = True

        self.target_effects = dict()
        self.apply_modifiers()
