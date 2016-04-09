import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Herd import *
from Environment import *
import math

class GUI(object):

	def __init__(self, x, y, width, height, color=(0.5,0.5,0.5,0.5), hovercolor=(0.7,0.7,0.7,0.7), presscolor=(1,1,1,0.7), text=""):
		self.pressed = False
		self.hovered = False
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.color = color
		self.hovercolor = hovercolor
		self.presscolor = presscolor
		self.text = text

	def clicked(self, x, y):
		return (self.x < x < self.x + self.width and
				self.y < y < self.y + self.height)

	def mouse_press(self, x, y):
		return

	def mouse_drag(self, x, y):
		return

	def mouse_release(self, x, y):
		return

	def mouse_motion(self, x, y):
		return

class Button(GUI):

	def __init__(self, f, **kwargs):
		super(Button, self).__init__(**kwargs)
		self.f = f
		self.label = pyglet.text.Label(self.text, font_size=30, x=self.x+self.width/2, y=self.y+self.height/2, 
			anchor_x="center", anchor_y="center")

	def draw(self):
		if self.pressed:
			drawSquare(self.x, self.y, self.width, self.height, self.presscolor)
		elif self.hovered:
			drawSquare(self.x, self.y, self.width, self.height, self.hovercolor)
		else:
			drawSquare(self.x, self.y, self.width, self.height, self.color)
		self.label.draw()

	def mouse_press(self, x, y):
		if self.clicked(x, y):
			self.pressed = True
		return self.pressed

	def mouse_drag(self, x, y):
		if self.clicked(x, y):
			self.pressed = True
		else:
			self.pressed = False
			self.hovered = False
		return self.pressed

	def mouse_release(self, x, y):
		if self.pressed:
			self.pressed = False
			self.f()

	def mouse_motion(self, x, y):
		if self.clicked(x, y):
			self.hovered = True
		else:
			self.hovered = False

class Group(GUI):
	
	def __init__(self, **kwargs):
		super(Group, self).__init__(**kwargs)

	def draw(self):
		drawSquare(self.x, self.y, self.width, self.height, self.color)


class ButtonIndicator(GUI):

	def __init__(self, **kwargs):
		super(Group, self).__init__(**kwargs)

	def draw(self):
		drawSquare(self.x, self.y, self.width, self.height, self.color)


def drawSquare(x, y, width, height, color):
	vertices = (x, y, 0,
				x+width, y, 0,
				x+width, y+height, 0,
				x, y+height, 0)
	glColor4f(*color)
	pyglet.graphics.vertex_list(4, ("v3f/static", vertices)).draw(GL_QUADS)