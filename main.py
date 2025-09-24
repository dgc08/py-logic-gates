#!/usr/bin/env python3
from pgnull import *

from component import *

game = pgnull.Game()
game.init_screen(600, 800, "py logic gates", pygame.RESIZABLE)

class GuiElements(GameObject):
    def on_start(self):
        self.static = True
        self.reg_obj(TextBox("q: XOR  w: AND  e: OR   r: NOT\na: inp  s: out\nx: delete", pos=(200,50)))

class MainScreen(GameObject):
    def on_start(self):
        #self.bg_color = (136, 136, 136)
        self.reg_obj(Sprite("bg.png", tile=True))
        self.reg_obj(GuiElements())

        self.reg_obj(ComponentContainer(), "c")

game.run_game(MainScreen())
