import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Herd import *
from Environment import *
import math

# ================ TODO================
# * Write label widget


class GUI(object):

	def __init__(self):
		pass

#	def mouse_press(self, x, y):
#		pass
#
#	def mouse_drag(self, x, y):
#		pass
#
#	def mouse_release(self, x, y):
#		pass
#
#	def mouse_motion(self, x, y):
#		pass

class Button(GUI):
	# Button class that is placed on a panel, reacts to mouse events, and calls a function when pressed

	def __init__(self, panel, anchor, f, icon, text="",
			color=(0,0,0,0), hovercolor=(1,1,1,0.1), presscolor=(1,1,1,0.5)):
		self.panel = panel
		self.anchor = anchor # left, center, or right
		self.f = f
		self.text = text
		self.sprite = pyglet.sprite.Sprite(icon)

		self.pressed = False
		self.hovered = False

		self.color = color
		self.hovercolor = hovercolor
		self.presscolor = presscolor

		if self.text != "":
			self.label = pyglet.text.Label(self.text, font_size=12, font_name="Roboto", anchor_x="center", anchor_y="center")
		
		self.panel.addButton(self)


	def clicked(self, x, y):
		return (self.x < x < self.x + self.width and
				self.y < y < self.y + self.height)



class Label(GUI):

	def __init__(self, panel, anchor, text=""):
		self.panel = panel
		self.anchor = anchor
		self.text = text



class BottomPanel(GUI):
	# At bottom of screen, handles multiple buttons, their drawing and position

	def __init__(self, width, height, color=(0.05,0.05,0.05,0.8)):
		self.color = color
		self.buttons = []
		self.leftButtons = []
		self.centerButtons = []
		self.rightButtons = []

		self.width = width
		self.height = height
		self.buttonWidth = height
		self.margin = 0 #pixels

		self.iconBatch = pyglet.graphics.Batch()

	def addButton(self, button):
		self.buttons.append(button)
		if button.anchor == "left":
			self.leftButtons.append(button)
		elif button.anchor == "center":
			self.centerButtons.append(button)
		elif button.anchor == "right":
			self.rightButtons.append(button)
		# Add button icon sprite to batch
		button.sprite.batch = self.iconBatch
		# Update layout
		self.layoutPanel()

	def layoutPanel(self):
		# Location specific configuration
		for i in range(len(self.leftButtons)):
			button = self.leftButtons[i]
			button.x = self.buttonWidth * i
		for i in range(len(self.centerButtons)):
			button = self.centerButtons[i]
			button.x = self.width/2 - (len(self.centerButtons) * self.buttonWidth / 2) + self.buttonWidth * i
		for i in range(len(self.rightButtons)):
			button = self.rightButtons[i]
			button.x = self.width - (len(self.rightButtons) - i) * self.buttonWidth

		# Location general configuration
		for button in self.buttons:
			button.y = self.margin
			button.width = self.buttonWidth
			button.height = self.height - self.margin * 2
			if button.text != "":
				button.label.x = button.x + button.width/2
				button.label.y = button.height/4
				button.sprite.x = button.x + button.width/2
				button.sprite.y = button.y + button.height*2/3
			else:
				button.sprite.x = button.x + button.width/2
				button.sprite.y = button.y + button.height/2
	

	def draw(self):
		vertices = tuple()
		colors = tuple()
		vertices += getSquareVertices(0, 0, self.width, self.height)
		colors += self.color * 4
		for button in self.buttons:
			vertices += getSquareVertices(button.x, button.y, button.width, button.height)
			if button.pressed:
				colors += button.presscolor * 4
			elif button.hovered:
				colors += button.hovercolor * 4
			else:
				colors += button.color * 4
		pyglet.graphics.vertex_list(4 * (len(self.buttons) + 1), ("v3f/static", vertices), ("c4f/static", colors)).draw(GL_QUADS)
		# Draw labels on top of buttons
		for button in self.buttons:
			if button.text != "":
				button.label.draw()
		# Draw icons on buttons
		self.iconBatch.draw()


	def mouse_press(self, x, y):
		if y < self.height:
			for button in self.buttons:
				if button.clicked(x, y):
					button.pressed = True
					return True
		return False

	def mouse_drag(self, x, y):
		for button in self.buttons:
			if button.clicked(x, y) and button.pressed:
				button.pressed = True
				return True
			else:
				button.pressed = False
				button.hovered = False
		return False

	def mouse_release(self, x, y):
		if y < self.height:
			for button in self.buttons:
				if button.pressed:
					button.pressed = False
					button.f()

	def mouse_motion(self, x, y):
		for button in self.buttons:
			if button.clicked(x, y):
				button.hovered = True
			else:
				button.hovered = False



class RightPanel():

	def __init__(self, text=""):
		pass



def getSquareVertices(x, y, width, height):
	vertices = (x, y, 0,
				x+width, y, 0,
				x+width, y+height, 0,
				x, y+height, 0)
	return vertices
