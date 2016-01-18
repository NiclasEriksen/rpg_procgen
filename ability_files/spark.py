

class Spark(UsableAbility):

    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.ability_attr["name"] = "Spark"
        self.ability_attr["magic_type"] = "electric"
        self.ability_attr["lvl"] = 1
        self.ability_attr["cost"] = 20
        self.ability_attr["cost_type"] = "mp"
        self.ability_attr["cast_time"] = 0.5
        self.ability_attr["range"] = 500
        self.ability_attr["hit_range"] = 50
        self.use_effect = "Electric 9"
        self.use_effect_scale = 1.0

        self.target_effects_base["dmg"] = 150
        self.target_effects_base["dmg_type"] = self.ability_attr["magic_type"]
        self.target_effects = dict()
        self.apply_modifiers()

    def custom_action(self, target):
        dist = get_dist(self.owner.x, self.owner.y, *target)
        if dist <= self.ability_attr["range"]:
            if self.do_cost():
                animpos = self.owner.window.get_windowpos(
                    *target, precise=True
                )
                self.owner.window.animator.spawn_anim(
                    self.use_effect, animpos, scale=self.use_effect_scale
                )
                for e in self.owner.game.enemies:
                    dist = get_dist(*target, e.x, e.y)
                    if dist <= self.ability_attr["hit_range"]:
                        dmgscale = 1.0 - dist / self.ability_attr["hit_range"] * 0.75
                        eff = self.target_effects.copy()
                        eff["dmg"] = self.target_effects["dmg"] * dmgscale
                        e.do_effect(eff)
