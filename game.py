from main import logger
from tiles import TiledRenderer
from player import Player
from enemy import Enemy


class Game:

    def __init__(self, window):
        self.window = window

    def newgame(self, level):
        self.tiles = TiledRenderer(self.window, level)
        self.player = Player(window=self.window, x=50, y=50)
        self.enemy = Enemy(window=self.window, x=200, y=100)
