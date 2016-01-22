from pyglet.sprite import Sprite
from pyglet.text import Label
from pyglet import gl
from pyglet import graphics
from functions import *


class UI:

    def __init__(self, window):
        self.window = window
        self.buttons = []
        self.bars = []
        self.progressbars = []
        self.combat_text = []
        self.auto_target_rings = []
        self.target_rings = []
        self.target_label = None
        self.stats = None
        self.settings = dict(
            draw_mob_hp=True,
            allways_draw_mob_hp=False,
            redraw_time=0.5
        )
        self.redraw_timer = self.settings["redraw_time"]
        self.bg_batch = self.window.batches["gui1"]
        self.fg_batch = self.window.batches["gui2"]
        self.bar_fg_batch = self.window.batches["gui3"]
        self.behind_batch = self.window.batches["gui0"]

    def add_button(
        self, x, y, text="Default",
        cb=None, cb_arg=None
    ):
        button = Button(
            self.window, x=x, y=y, text=text, callback=cb, callback_arg=cb_arg,
            bg_batch=self.bg_batch, fg_batch=self.fg_batch
        )
        self.buttons.append(button)

    def add_bar(
        self, x, y,
        text="Default", width=200, height=30, color="blue", shows="default"
    ):
        bar = Bar(
            self.window,
            x=x, y=y,
            text=text, w=width, h=height, c=color, s=shows,
            bg_batch=self.bg_batch, fg_batch=self.bar_fg_batch
        )
        self.bars.append(bar)

    def add_progressbar(
        self, x, y, duration, w=64, h=10, title=None,
        c="blue", bgc="dblue", tc="black"
    ):
        b = ProgressBar(
            self.window, x=x, y=y, w=w, h=h, c=c, bgc=bgc, tc=tc,
            duration=duration,
            fg_batch=self.fg_batch, title=title
        )
        self.progressbars.append(b)

    def add_stats(self, owner, x, y, width, height):
        self.stats = Stats(
            self.window, owner, x=x, y=y, w=width, h=height,
            bg_batch=self.bg_batch, fg_batch=self.fg_batch,
        )

    def add_combat_text(self, text, x, y, **kwargs):
        ct = FloatingCombatText(
            self, text, x, y, batch=self.fg_batch, **kwargs
        )
        self.combat_text.append(ct)

    def update_bar(self, bartype, value, maxvalue):
        for b in self.bars:
            if b.type == bartype:
                b.update(value, maxvalue)

    def update_stats(self):
        if self.stats and self.window.debug:
            self.stats.update()

    def check(self, x, y, press=True, dry=False):
        if dry:
            for b in self.bars:
                if b.check(x, y):
                    return True
            for b in self.buttons:
                if b.check(x, y):
                    return True
            if self.stats:
                if self.stats.check(x, y):
                    return True
        else:
            for b in self.bars:
                if b.check(x, y):
                    return True
            for b in self.buttons:
                if press:
                    if b.check(x, y):
                        b.press()
                        return True
                else:
                    if b.pressed:
                        if b.check(x, y):
                            b.release()
                            return True
                        else:
                            b.release(do_action=False)
            if self.stats:
                if self.stats.check(x, y):
                    return True

            return False

    def update(self, dt):
        if self.redraw_timer >= self.settings["redraw_time"]:
            if self.window.game.player:
                p = self.window.game.player
                self.update_bar("hp", int(p.hp), p.max_hp)
                self.update_bar("mp", int(p.mp), p.max_mp)
                self.update_bar("sta", int(p.sta), p.max_sta)
                self.update_stats()
            self.redraw_timer = 0
        else:
            self.redraw_timer += dt

        if self.stats:
            if self.window.debug and self.stats.hidden:
                self.stats.toggle_hide(False)
            elif not self.window.debug and not self.stats.hidden:
                self.stats.toggle_hide(True)

        p = self.window.game.player
        if p:
            if p.cast_object:
                if not self.progressbars:
                    barpos = self.window.get_windowpos(p.x, p.y + 24)
                    fg_c, bg_c, tc = get_color_scheme_by_type(
                        p.cast_object.ability.ability_attr["magic_type"]
                    )
                    self.add_progressbar(
                        *barpos, p.cast_object.time,
                        w=40, h=6, c=fg_c, bgc=bg_c, tc=tc,
                        title=p.cast_object.ability.get_name()
                    )
                else:
                    for b in self.progressbars:
                        b.update(p.cast_object.timer)
            else:
                for b in self.progressbars:
                    b.label.delete()
                    if hasattr(b, "title"):
                        b.title.delete()
                self.progressbars = []

            t = p.target
            if t:
                if not self.target_rings:
                    tr = TargetRing(
                        self.window, t.x, t.y,
                        w=t.sprite.width, h=t.sprite.height,
                        batch=self.behind_batch
                    )
                    self.target_rings.append(tr)
                else:
                    for r in self.target_rings:
                        r.update(t.x, t.y)

                if not self.target_label:
                    self.target_label = Label(
                        text=t.name, font_name=None, font_size=12,
                        x=self.window.width // 2, y=100,
                        anchor_x="center", anchor_y="center",
                        color=(0, 0, 0, 255)
                    )
                else:
                    self.target_label.text = t.name
            else:
                if self.target_rings:
                    for r in self.target_rings:
                        r.sprite.delete()
                    self.target_rings = []
                if self.target_label:
                    self.target_label = None

        else:
            for b in self.progressbars:
                b.label.delete()
                if hasattr(b, "title"):
                    b.title.delete()
            self.progressbars = []

        for ct in self.combat_text:
            ct.update(dt)

    def draw(self):
        if self.settings["draw_mob_hp"]:
            gl.glColor4f(*lookup_color("red", gl=True))
            gl.glLineWidth(3)
            for e in self.window.game.enemies:
                if e.hp < e.max_hp or self.settings["allways_draw_mob_hp"]:
                    wpos = self.window.get_windowpos(
                        e.x, e.y + e.sprite.height,
                        check=True, tol=32, precise=True
                    )
                    if wpos:
                        width = (e.hp / e.max_hp) * e.sprite.width
                        graphics.draw(
                            2,
                            gl.GL_LINES,
                            (
                                'v2f',
                                (
                                    wpos[0] - width / 2,
                                    wpos[1],
                                    wpos[0] + width / 2,
                                    wpos[1])
                                )
                        )

        # for b in self.buttons:
        #     b.draw()
        self.bg_batch.draw()
        if self.window.game.player:
            for b in self.bars:
                b.draw()
            self.bar_fg_batch.draw()
        if self.stats:
            self.stats.draw()
        for b in self.progressbars:
            b.draw()
        self.fg_batch.draw()
        if self.target_label:
            self.target_label.draw()


class TargetRing:

    def __init__(self, window, x, y, w=32, h=32, batch=None):
        self.window = window
        self.x, self.y = window.get_windowpos(x, y, precise=True)
        self.gamepos = (x, y)
        img = window.textures["redcircle"]
        scale = w / img.width
        self.sprite = Sprite(
            img,
            x=self.x, y=self.y,
            batch=batch
        )
        self.sprite.scale = scale

    def update(self, x, y):
        w = self.window
        self.sprite.x, self.sprite.y = self.x, self.y = w.get_windowpos(
            x, y, precise=True
        )


class Button:

    def __init__(
        self, window, x=20, y=20, text="Default",
        callback=None, callback_arg=None,
        bg_batch=None, fg_batch=None
    ):
        self.window = window
        self.img = window.textures["button"]
        self.img_down = window.textures["button_down"]
        self.sprite = Sprite(self.img, x=x, y=y, batch=bg_batch)
        self.label = Label(
            text=text, font_name=None, font_size=10,
            x=x, y=y, anchor_x="center", anchor_y="center",
            color=(0, 0, 0, 255), batch=fg_batch
        )

        self.width, self.height = self.img.width, self.img.height
        self.x, self.y = x, y

        self.pressed = False
        self.callback = callback
        self.callback_arg = callback_arg

    def set_pos(self, x, y):
        self.sprite.x, self.sprite.y = x, y
        self.label.x, self.label.y = x, y
        self.x, self.y = x, y

    def press(self):
        self.pressed = True
        self.sprite.image = self.img_down

    def release(self, do_action=True):
        self.pressed = False
        self.sprite.image = self.img
        if do_action:
            if self.callback_arg:
                self.callback(self.callback_arg)
            else:
                self.callback()

    def check(self, x, y):
        if (
            x >= self.x - self.width / 2 and
            x < self.x + self.width / 2 and
            y >= self.y - self.height / 2 and
            y < self.y + self.height / 2
        ):
            return True
        else:
            return False

    def draw(self):
        pass


class Bar:

    def __init__(
        self, window, x=20, y=20,
        text="Default", w=100, h=20, c="blue", s="default",
        bg_batch=None, fg_batch=None
    ):
        self.window = window
        self.color = lookup_color(c, gl=True)
        self.label = Label(
            text=text, font_name=None, font_size=9,
            x=x, y=y, anchor_x="center", anchor_y="center",
            color=(255, 255, 255, 255), batch=fg_batch
        )

        self.width, self.height = w, h
        self.x, self.y = x, y
        self.value = 100
        self.type = s
        self.value_max = 100
        self.update(self.value, self.value_max)

    def set_pos(self, x, y):
        self.sprite.x, self.sprite.y = x, y
        self.label.x, self.label.y = x, y
        self.x, self.y = x, y

    def check(self, x, y):
        if (
            x >= self.x - self.width / 2 and
            x < self.x + self.width / 2 and
            y >= self.y - self.height / 2 and
            y < self.y + self.height / 2
        ):
            return True
        else:
            return False

    def update(self, value, maxvalue):
        self.value_max = maxvalue
        if not self.value == value:
            self.value = value
            w = self.width * (self.value / self.value_max)
            self.rectangle = create_rectangle(
                self.x - self.width / 2, self.y + self.height / 2,
                w, self.height,
                centered=False
            )
            self.label.x = int((self.x - self.width / 2) + w / 2)
            self.label.text = str(value)

    def draw(self):
        try:
            gl.glEnable(gl.GL_BLEND)
            gl.glColor4f(*self.color)
            graphics.draw(4, gl.GL_QUADS, ('v2f', self.rectangle))
            gl.glDisable(gl.GL_BLEND)
            # self.label.draw()
        except AttributeError as e:
            self.window.logger.debug(
                "Bar is not ready to be drawn: {0}".format(e)
            )


class FloatingCombatText:

    def __init__(
        self, ui, text, x, y, duration=1.,
        scale=1., second_scale=0.5, growth=0.2, velocity=75,
        color="darkred", batch=None
    ):
        self.start_scale = scale
        self.second_scale = second_scale
        self.growth = growth
        self.x, self.y = x, y
        self.ui = ui
        wx, wy = self.ui.window.get_windowpos(x, y)
        self.color = lookup_color(color)
        self.label = Label(
            text=str(text), font_name=None, font_size=12 * scale,
            x=wx, y=wy, anchor_x="center", anchor_y="center",
            color=self.color, batch=batch,
        )
        self.velocity = velocity
        self.timer = duration
        self.duration = duration
        self.done = False

    def on_end(self):
        self.label.delete()
        self.done = True

    def update(self, dt):
        if self.timer <= 0:
            self.on_end()
        else:
            self.timer -= dt
            perc = self.timer / self.duration
            scale = (
                self.second_scale + (
                    (self.start_scale - self.second_scale) * perc
                )
            )
            self.y += self.velocity * dt
            self.label.font_size = 9 * scale
            self.label.x, self.label.y = self.ui.window.get_windowpos(
                self.x, self.y, precise=True
            )
            opacity = int(255 * perc)
            if opacity < 0:
                opacity = 0
            self.color = self.color[0], self.color[1], self.color[2], opacity
            self.label.color = self.color


class ProgressBar:

    def __init__(
        self, window, x=20, y=20, duration=1.,
        text="Default", w=64, h=20, c="blue", bgc="dblue", tc="black",
        bg_batch=None, fg_batch=None, title=None
    ):
        self.window = window
        self.text_color = lookup_color(tc)
        self.color = lookup_color(c, gl=True)
        self.bg_color = lookup_color(bgc, gl=True)
        self.width, self.height = w, h
        self.x, self.y = x, y
        self.value = 0
        self.value_max = duration
        self.update(self.value)
        self.bg_rectangle = create_rectangle(
            x - w / 2, y + h / 2,
            w, h,
            centered=False
        )
        self.label = Label(
            text=str(self.value_max), font_name=None, font_size=7,
            x=x, y=y, anchor_x="center", anchor_y="center",
            color=self.text_color, batch=fg_batch
        )
        if title:
            self.title = Label(
                text=title, font_name=None, font_size=7,
                x=x, y=y + 10, anchor_x="center", anchor_y="center",
                color=(255, 255, 255, 255), batch=fg_batch
            )

    def update(self, value):
        if not self.value == value:
            self.value = value
            w = self.width * (self.value / self.value_max)
            self.rectangle = create_rectangle(
                self.x - self.width / 2, self.y + self.height / 2,
                w, self.height,
                centered=False
            )
            self.label.text = str(round(self.value_max - self.value, 1))

    def draw(self):
        try:
            gl.glEnable(gl.GL_BLEND)
            gl.glColor4f(*self.bg_color)
            graphics.draw(4, gl.GL_QUADS, ('v2f', self.bg_rectangle))
            gl.glColor4f(*self.color)
            graphics.draw(4, gl.GL_QUADS, ('v2f', self.rectangle))
            gl.glDisable(gl.GL_BLEND)
            # self.label.draw()
        except AttributeError as e:
            self.window.logger.debug(
                "Bar is not ready to be drawn: {0}".format(e)
            )


class Stats:

    def __init__(
        self, window, owner, x=50, y=200, w=180, h=300,
        bg_batch=None, fg_batch=None, hidden=True
    ):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.bg_batch, self.fg_batch = bg_batch, fg_batch
        self.owner, self.window = owner, window
        self.color = lookup_color("grey", gl=True)
        self.hidden = hidden
        self.build()

    def check(self, x, y):
        if (
            x >= self.x - self.width / 2 and
            x < self.x + self.width / 2 and
            y >= self.y - self.height / 2 and
            y < self.y + self.height / 2
        ):
            return True
        else:
            return False

    def build(self):
        if not self.hidden and self.window.debug:
            batch = self.fg_batch
            self.stat_labels_l = []
            self.stat_labels_r = []
            y = self.y
            yo = 0
            x = self.x
            mainstat = self.owner.mainstat
            if mainstat == "str":
                c = lookup_color("darkred")
            elif mainstat == "agi":
                c = lookup_color("darkgreen")
            elif mainstat == "int":
                c = lookup_color("darkblue")
            else:
                c = lookup_color("yellow")
            label_l = Label(
                text="Main stat:", font_name=None, font_size=10,
                x=x, y=y-yo, anchor_x="left", anchor_y="top",
                color=lookup_color("black"), batch=batch
            )
            label_r = Label(
                text=mainstat, font_name=None, font_size=10,
                x=x+self.width, y=y-yo,
                anchor_x="right", anchor_y="top",
                color=c, batch=batch
            )
            self.stat_labels_l.append(label_l)
            self.stat_labels_l.append(label_r)
            yo += 16

            for stat, value in self.owner.base_stats.items():
                modvalue = self.owner.stats.get(stat)
                label_l = Label(
                    text=str(stat), font_name=None, font_size=8,
                    x=x, y=y-yo, anchor_x="left", anchor_y="top",
                    color=lookup_color("black", opacity=255),
                    batch=batch
                )
                label_r = Label(
                    text=str(modvalue), font_name=None, font_size=8,
                    x=x+self.width, y=y-yo,
                    anchor_x="right", anchor_y="top",
                    color=lookup_color("darkblue", opacity=255),
                    batch=batch
                )
                label_r.identifier = str(stat)
                self.stat_labels_l.append(label_l)
                self.stat_labels_r.append(label_r)
                yo += 12
            self.height = yo
            self.rectangle = create_rectangle(
                self.x, self.y,
                self.width, self.height,
                centered=False
            )

    def toggle_hide(self, hidden):
        print("Hidden: {0}".format(hidden))
        if hidden:
            self.hidden = True
            for l in self.stat_labels_l:
                l.delete()
            for l in self.stat_labels_r:
                l.delete()
            self.stat_labels_l = []
            self.stat_labels_r = []
        else:
            self.hidden = False
            self.build()

    def update(self):
        for bs, value in self.owner.stats.get_all_stats().items():
            for l in self.stat_labels_r:
                if l.identifier == bs:
                    value = round(self.owner.stats.get(bs), 1)
                    l.text = str(value)
                    break

    def draw(self):
        if self.window.debug and not self.hidden:
            gl.glColor4f(*self.color)
            graphics.draw(4, gl.GL_QUADS, ('v2f', self.rectangle))
            if not self.fg_batch:
                for l in self.stat_labels_l:
                    l.draw()
                for l in self.stat_labels_r:
                    l.draw()
