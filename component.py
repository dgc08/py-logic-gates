#!/usr/bin/env python3

from pgnull import *
import copy

class Connection(GameObject):
    def __init__(self, component, is_src):
        super().__init__()
        self.color = (0,0,150)
        if is_src:
            self.source = component
            self.target = None
        else:
            self.target = component
            self.source = None
        self.abort = False

    def on_start(self):
        self.finding = True
        self.parent.finding_connection = self

    def on_mouse_down(self, pos, button):
        if button == 1 and self.finding:
            self.abort = True

    def destroy(self):
        if self.source:
            self.source.links.remove(self)
        if self.target:
            self.target.link = None

        self.dequeue()

    def on_update(self, ctx):
        if self.finding:
            if self.abort:
                self.parent.blocked = False
                self.parent.finding_connection = None
                self.destroy()
        else:
            self.target.value = self.source.value
            if self.source.value:
                self.color = (self.color[0], 255, self.color[2])
            else:
                self.color = (self.color[0], 0, self.color[2])

    def register_second(self, component, is_src):
        if (self.source and is_src) or (self.target and not is_src):
            print("Can't connect two inputs or two outputs")
            self.abort = True

        self.parent.blocked = False
        self.parent.finding_connection = None
        self.finding = False

        if is_src:
            self.source = component
        else:
            self.target = component

    def on_draw(self, ctx):
        if self.finding:
            if self.source:
                start_pos = self.source.last_draw_pos
            else:
                start_pos = self.target.last_draw_pos

            pygame.draw.line(Game.get_game().screen.pygame_obj, self.color, start_pos, ctx.mouse_pos, width=5)
        else:
            pygame.draw.line(Game.get_game().screen.pygame_obj, self.color, self.source.last_draw_pos, self.target.last_draw_pos, width=5)

class Input(Circle):
    def __init__(self, i):
        self.value = False
        self.index = i
        super().__init__(pos=(0,0), radius=5, color=[0,0,255])

    def destroy(self):
        if self.link:
            self.link.destroy()

    def on_start(self):
        self.link = None

    def change_color(self):
        if not self.link:
            return
        if self.link.color[2] == 150:
            self.link.color = (150,self.link.color[1],0)
        else:
            self.link.color = (0,self.link.color[1],150)

    def on_click(self):
        if not self.parent.parent.blocked:
            self.parent.parent.blocked = True
            l = self.parent.parent.reg_obj(Connection(self, False))

            if self.link:
                self.link.destroy()
            self.link = l
        elif self.parent.parent.finding_connection and not self.parent.parent.finding_connection == self.link:
            if self.link:
                self.link.destroy()
            self.link = self.parent.parent.finding_connection
            self.parent.parent.finding_connection.register_second(self, False)

class Output(Input):
    def on_start(self):
        self.links = []

    def destroy(self):
        for i in self.links:
            i.destroy()

    def change_color(self):
        for link in self.links:
            if link.color[2] == 150:
                link.color = (150,link.color[1],0)
            else:
                link.color = (0,link.color[1],150)

    def on_click(self):
        if not self.parent.parent.blocked:
            self.parent.parent.blocked = True
            l = self.parent.parent.reg_obj(Connection(self, True))

            self.links.append(l)
        elif self.parent.parent.finding_connection and not self.parent.parent.finding_connection == self.links[-1]:
            self.links.append(self.parent.parent.finding_connection)
            self.parent.parent.finding_connection.register_second(self, True)

class Component(GameObject):
    min_vec = Vector2(0,90)
    def __init__(self, spec):
        self.spec = spec
        self.moving = False
        super().__init__()

    def on_start(self):
        self.text = TextBox(" "+self.spec.display+" ", pos=(0,0))
        self.reg_obj(Box((0,0), (0,0), color=(114, 252, 176), outline=0), "box_bg")
        self.box_bg.size = clamp_vector(Vector2(self.text.width, self.text.height) + (15, 25), self.min_vec)
        self.box_bg.topleft = Vector2(self.box_bg.size) / -2

        self.reg_obj(Box(topleft=self.box_bg.topleft, size=self.box_bg.size, color=(0,0,0), outline=4), "box")
        self.reg_obj(self.text)

        self.box.on_click = self.on_click

        input_spacing = self.box.size[1] / (self.spec.inputs+1)
        output_spacing = self.box.size[1] / (self.spec.outputs+1)

        self.inputs = []
        self.outputs = []

        for i in range(self.spec.inputs):
            obj = Input(i)
            obj.pos.x = self.box.topleft[0]-1
            obj.pos.y = self.box.topleft[1]+(i+1)*input_spacing

            self.inputs.append(self.reg_obj(obj))
        for i in range(self.spec.outputs):
            obj = Output(i)
            obj.pos.x = self.box.topleft[0] + self.box.size[0] + 1
            obj.pos.y = self.box.topleft[1]+(i+1)*output_spacing

            self.outputs.append(self.reg_obj(obj))

    def change_color(self):
        for i in self.inputs:
            i.change_color()
        for i in self.outputs:
            i.change_color()

    def on_update(self, ctx):
        inputs = []
        for i in self.inputs:
            inputs.append(i.value)
        ret = self.spec.prog(*inputs)
        if type(ret) == bool:
            ret = [ret]
        if len(ret) != self.spec.outputs:
            raise Exception("Mismatch between output numer and actual returned number of outputs on "+self.spec.display)
        for i,val in enumerate(ret):
            self.outputs[i].value = val

    def on_draw(self, ctx):
        if self.moving:
            if ctx.keyboard.x:
                self.dequeue()
                for i in self.inputs+self.outputs:
                    i.destroy()
                self.parent.blocked = False
            self.pos += ctx.mouse_rel

    def on_mouse_up(self, pos, button):
        if button == 1 and self.moving:
            self.moving = False
            self.change_color()
            self.parent.blocked = False

    def on_click(self):
        if not self.parent.blocked:
            self.change_color()
            self.moving = True
            self.parent.blocked = True

class LED(Component):
    class LEDSpec:
        inputs = 1
        outputs = 0
        uid = "out"
        display = "<-"
    def __init__(self):
        super().__init__(self.LEDSpec)

    def on_update(self, ctx):
        if self.inputs[0].value:
            self.circle.color[1] = 255
        else:
            self.circle.color[1] = 120


    def on_start(self):
        self.reg_obj(Circle((0,0), 18, color=[120,120,120]), "circle")
        super().on_start()
        self.box.dequeue()
        self.box_bg.dequeue()

        self.circle.on_click = self.on_click
        self.inputs[0].pos.x = -self.circle.radius-1

class Button(Component):
    class LEDSpec:
        inputs = 0
        outputs = 1
        uid = "inp"
        display = "->"
    def __init__(self):
        super().__init__(self.LEDSpec)

    def on_update(self, ctx):
        pass

    def on_start(self):
        self.reg_obj(Box((0,0), (36,36), color=(120,120,120)), "box_new")
        super().on_start()
        self.box.dequeue()
        self.box_bg.dequeue()


        self.box_new.topleft = (-18, -18)
        self.box_new.on_click = self.on_click
        self.outputs[0].pos.x = self.box_new.size[0]/2+1

    def on_mouse_up(self, pos, button):
        super().on_mouse_up(pos, button)
        if button == 3 and pygame.Rect(self.box_new.last_draw_pos, self.box_new.size).collidepoint(pos):
            self.outputs[0].value = not self.outputs[0].value

            if self.outputs[0].value:
                self.box_new.color = (120,255,120)
            else:
                self.box_new.color = (120,120,120)

class Label(Component):
    class LEDSpec:
        inputs = 0
        outputs = 0
        uid = "text"
        display = "<-"
    def __init__(self, text):
        self.LEDSpec.display = text
        super().__init__(self.LEDSpec)
        #self.reg_obj(TextBox(text, pos=(0,0), font="DejaVuSansMono.ttf", fontsize=16), "text")

    def on_update(self, ctx):
        pass

    def on_start(self):
        super().on_start()
        self.box_bg.dequeue()
        self.box.size = Vector2(self.text.width, self.text.height) + (15, 15)
        self.box.topleft = Vector2(self.box.size) / -2

class Switch(Component):
    class LEDSpec:
        inputs = 2
        outputs = 2
        uid = "route"
        display = "-"
    def __init__(self):
        super().__init__(self.LEDSpec)

    def on_update(self, ctx):
        self.outputs[0].value = self.inputs[0].value
        self.outputs[1].value = self.inputs[1].value

    def on_start(self):
        self.reg_obj(Box((0,0), (36,36), color=(120,120,120)), "box_new")
        super().on_start()
        self.box.dequeue()
        self.box_bg.dequeue()


        self.box_new.topleft = (-18, -18)
        self.box_new.on_click = self.on_click
        self.outputs[0].pos.x = self.box_new.size[0]/2+1
        self.outputs[0].pos.y = 0

        self.outputs[1].pos.x = 0
        self.outputs[1].pos.y = self.box_new.size[0]/2+1

        self.inputs[0].pos.x = self.box_new.size[0]/-2+1
        self.inputs[0].pos.y = 0

        self.inputs[1].pos.x = 0
        self.inputs[1].pos.y = self.box_new.size[0]/-2+1


class ComponentContainer(GameObject):
    def __init__(self):
        super().__init__()
        self.components = []
        self.loaded = []
        self.blocked = False # block moving since child is already moving
        self.finding_connection = None
        self.new_comps = []

    def on_start(self):
        self.load_components()

    def load_components(self):
        from builtin_components import Xor,And,Or,Not

        self.loaded = [Xor,And,Or,Not]

    def on_update(self, ctx):
        if ctx.mouse[0] and not self.blocked:
            self.parent.pos += ctx.mouse_rel

    def on_key_down(self, key, key_code):
        if key == "q":
            self.new_comps.append(Component(self.loaded[0]))
        if key == "w":
            self.new_comps.append(Component(self.loaded[1]))
        if key == "e":
            self.new_comps.append(Component(self.loaded[2]))
        if key == "r":
            self.new_comps.append(Component(self.loaded[3]))

        if key == "a":
            self.new_comps.append(Button())
        if key == "s":
            self.new_comps.append(LED())
        if key == "d":
            self.new_comps.append(Switch())
        if key == "f":
            name = input("Label Name:")
            self.new_comps.append(Label(name))

    def on_draw(self, ctx):
        while self.new_comps:
            new = self.new_comps.pop(0)
            new.pos = ctx.mouse_pos - self.pos
            self.reg_obj(new)
