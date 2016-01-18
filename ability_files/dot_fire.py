

class FireDoT(DoT):

    def __init__(self, owner, dmg=100):
        time = 2.5
        tick = 0.5
        self.tick_effect = "Status 3"
        self.tick_effect_scale = 0.3
        super().__init__(owner, dmg, time, tick, atype="spell", dtype="fire")
        owner.active_effects.append(self)
