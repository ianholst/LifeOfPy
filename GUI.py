import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Herd import *
from Environment import *
import math

class GUI(pyglet.event.EventDispatcher):

	def __init__(self):
		super(GUI, self).__init__()

	def clickTest(self, x, y):
		return (self.x < x < self.x + self.width and
				self.y < y < self.y + self.height)


class Button(GUI):

	def __init__(self):
		super(Button, self).__init__()