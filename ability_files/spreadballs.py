

class SpreadBalls(MultiProjectileAbility):

    """Fires three projectiles that pierce targets."""

    def __init__(self, owner):
        super().__init__()
        self.owner = owner

        self.ability_attr["lvl"] = 1
        self.ability_attr["name"] = "Spreadballs"
        self.ability_attr["type"] = "spell"
        self.ability_attr["magic_type"] = "electric"
        self.ability_attr["cost_type"] = "mp"
        self.ability_attr["cost"] = 10
        self.ability_attr["range"] = 250
        self.ability_attr["speed"] = 500
        self.ability_attr["penetration"] = 1

        self.spread = 15    # Degrees
        self.projectile_count = 3

        self.target_effects_base["dmg"] = 75
        self.target_effects_base["dmg_type"] = "electric"

        self.target_effects = dict()
        self.apply_modifiers()
        self.projectile_tex = self.owner.game.window.get_texture("bolt")
        self.projectile_tex.scale = 0.2
        # self.projectile_tex_scale = 0.3
        self.impact_anim = "Cataclysm"
        self.impact_anim_scale = 0.2
