

class Blink(UsableAbility):

    def __init__(self, owner):
        super().__init__()
        self.owner = owner

        self.ability_attr["name"] = "Blink"
        self.ability_attr["lvl"] = 1
        self.ability_attr["cost"] = 15
        self.ability_attr["cost_type"] = "sta"
        self.ability_attr["cooldown"] = 10
        self.ability_attr["range"] = 200

        self.level_scale_attr = dict(
            range=[200, 250, 300],
            cost=[15, 30, 45],
            cooldown=[10, 8, 6]
        )

        self.use_effect = "Magic 6"
        self.use_effect_scale = 0.5

    def custom_action(self, target):
        source = self.owner.x, self.owner.y
        dist = get_dist(*source, *target)
        if dist <= self.ability_attr["range"]:
            logging.info("Player blinking to {0}".format(target))
            if self.do_cost():
                pos = self.owner.get_windowpos()
                self.owner.window.animator.spawn_anim(
                    self.use_effect, pos, scale=self.use_effect_scale
                )
                self.owner.movement.set_pos(target)
                pos = self.owner.get_windowpos()
                self.owner.window.animator.spawn_anim(
                    self.use_effect, pos, scale=self.use_effect_scale
                )
