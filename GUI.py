import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Herd import *
from Environment import *
from Models import *
import math

# ================ TODO================
# Write label widget
# Right panel

class GUI:
	# Holds GUI resources
	pyglet.resource.path = ["resources"]
	pyglet.resource.reindex()

	playIcon = pyglet.resource.image("play.png")
	pauseIcon = pyglet.resource.image("pause.png")
	slowerIcon = pyglet.resource.image("slower.png")
	fasterIcon = pyglet.resource.image("faster.png")
	plusIcon = pyglet.resource.image("plus.png")
	settingsIcon = pyglet.resource.image("settings.png")
	threeDIcon = pyglet.resource.image("3d.png")
	noIcon = pyglet.resource.image("none.png")

	for icon in [playIcon,pauseIcon,slowerIcon,fasterIcon,noIcon,threeDIcon,plusIcon,settingsIcon]:
		icon.anchor_x = icon.width/2
		icon.anchor_y = icon.height/2

	# Colors
	buttonColor = (0,0,0,0)
	buttonHoverColor = (1,1,1,0.1)
	buttonPressColor = (1,1,1,0.5)
	panelColor = (0.05,0.05,0.05,0.8)



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

class Button:
	# Button class that is placed on a panel, reacts to mouse events, and calls a function when pressed

	def __init__(self, panel, anchor, f, icon,
			color=GUI.buttonColor, hovercolor=GUI.buttonHoverColor, presscolor=GUI.buttonPressColor):
		self.panel = panel
		self.anchor = anchor # left, center, or right
		self.f = f
		self.sprite = pyglet.sprite.Sprite(icon)

		self.pressed = False
		self.hovered = False

		self.color = color
		self.hovercolor = hovercolor
		self.presscolor = presscolor

		self.panel.addButton(self)


	def clicked(self, x, y):
		return (self.x < x < self.x + self.width and
				self.y < y < self.y + self.height)



class Label:

	def __init__(self, panel, anchor, width, text=""):
		self.panel = panel
		self.anchor = anchor
		self.width = width
		self.text = text
		#	self.label = pyglet.text.Label(self.text, font_size=12, font_name="Roboto", anchor_x="center", anchor_y="center")



class BottomPanel:
	# At bottom of screen, handles multiple buttons, their drawing and position

	def __init__(self, width, height, color=GUI.panelColor):
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
			button.sprite.x = button.x + button.width/2
			button.sprite.y = button.y + button.height/2

		# Rebuild vertices
		vertices = []
		vertices += Models.square(0, 0, self.width, self.height)
		for button in self.buttons:
			vertices += Models.square(button.x, button.y, button.width, button.height)
		self.panelModel = pyglet.graphics.vertex_list(4 * (len(self.buttons) + 1), ("v3f", vertices), "c4f")
		self.updateColors()


	def updateColors(self):
		colors = []
		colors += self.color * 4
		for button in self.buttons:
			if button.pressed:
				colors += button.presscolor * 4
			elif button.hovered:
				colors += button.hovercolor * 4
			else:
				colors += button.color * 4
		self.panelModel.colors = colors


	def draw(self):
		self.panelModel.draw(GL_QUADS)
		# Draw icons on buttons
		self.iconBatch.draw()


	def mouse_press(self, x, y):
		if y < self.height:
			for button in self.buttons:
				if button.clicked(x, y):
					button.pressed = True
					self.updateColors()
					return True
		return False

	def mouse_drag(self, x, y):
		for button in self.buttons:
			if button.clicked(x, y) and button.pressed:
				button.pressed = True
				self.updateColors()
			else:
				button.pressed = False
				button.hovered = False
				self.updateColors()

	def mouse_release(self, x, y):
		if y < self.height:
			for button in self.buttons:
				if button.pressed:
					button.pressed = False
					self.updateColors()
					button.f()


	def mouse_motion(self, x, y):
		for button in self.buttons:
			if button.clicked(x, y):
				button.hovered = True
				self.updateColors()
			else:
				button.hovered = False
				self.updateColors()



class RightPanel:

	def __init__(self, width, title=""):
		self.width = width
		self.title = title



if __name__ == '__main__':
	from Main import main
	main()