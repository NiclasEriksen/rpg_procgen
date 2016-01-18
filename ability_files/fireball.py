

class FireBall(ProjectileAbility):

    """Simple fireball with aoe effect."""

    def __init__(self, owner):
        super().__init__()
        self.owner = owner

        self.ability_attr["lvl"] = 1
        self.ability_attr["name"] = "Fireball"
        self.ability_attr["type"] = "spell"
        self.ability_attr["magic_type"] = "fire"
        self.ability_attr["cost_type"] = "mp"
        self.ability_attr["cost"] = 5
        self.ability_attr["range"] = 400
        self.ability_attr["speed"] = 350
        self.ability_attr["cast_time"] = 1.0
        self.ability_attr["move_interrupt"] = True

        self.target_effects_base["dmg"] = 60
        self.target_effects_base["dmg_type"] = "fire"
        self.target_effects_base["aoe"] = 50
        self.target_effects_base["aoe_dmg"] = 30
        self.target_effects_base["dot"] = FireDoT
        self.target_effects_base["dot_dmg"] = 60

        self.target_effects = dict()
        self.apply_modifiers()
        self.projectile_tex = self.owner.game.window.get_texture("fireball2")
        self.projectile_tex.scale = 0.3
        self.impact_anim = "Fire 3"
        self.projectile_anim = "Fireball"
        self.projectile_anim_scale = 0.3
