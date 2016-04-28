import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Models import *

#================== TODO ==================#
# Write label widget
# Right panel

class GUI:
	# Utility class: Holds GUI resources
	pyglet.resource.path = ["resources"]
	pyglet.resource.reindex()

	# Icons
	playIcon = pyglet.resource.image("play.png")
	pauseIcon = pyglet.resource.image("pause.png")
	slowerIcon = pyglet.resource.image("slower.png")
	fasterIcon = pyglet.resource.image("faster.png")
	plusIcon = pyglet.resource.image("plus.png")
	settingsIcon = pyglet.resource.image("settings.png")
	threeDIcon = pyglet.resource.image("3d.png")
	noIcon = pyglet.resource.image("none.png")
	creatureIcon = pyglet.resource.image("creature.png")
	treeIcon = pyglet.resource.image("tree.png")

	for icon in [playIcon,pauseIcon,slowerIcon,fasterIcon,noIcon,threeDIcon,plusIcon,settingsIcon,creatureIcon,treeIcon]:
		icon.anchor_x = icon.width/2
		icon.anchor_y = icon.height/2

	# Colors
	panelColor = (0.05,0.05,0.05,0.8)
	buttonColor = (0,0,0,0)
	buttonHoverColor = (1,1,1,0.1)
	buttonPressColor = (1,1,1,0.5)

	# Fonts
	font = "Calibri"
	fontSize = 12
	titleFontSize = 30

	# Panels
	buttonSize = 80
	bottomPanelHeight = 80
	rightPanelWidth = 400
	rightPanelMargin = 20


class Button:
	# Button class that is placed on a panel, reacts to mouse events, and calls a function when pressed

	def __init__(self, anchor="left", f=None, icon=GUI.noIcon, text="", color=GUI.buttonColor, hovercolor=GUI.buttonHoverColor, presscolor=GUI.buttonPressColor):
		self.anchor = anchor # left, center, or right
		self.f = f
		self.sprite = pyglet.sprite.Sprite(icon)

		self.pressed = False
		self.hovered = False

		self.text = text
		if self.text != "":
			self.label = pyglet.text.Label(self.text, font_size=GUI.fontSize, font_name=GUI.font, anchor_x="center", anchor_y="center")

		self.color = color
		self.hovercolor = hovercolor
		self.presscolor = presscolor


	def clicked(self, x, y):
		return (self.x < x < self.x + self.width and
				self.y < y < self.y + self.height)



class Label:

	def __init__(self, anchor, width, text=""):
		self.anchor = anchor
		self.width = width
		self.text = text
		self.label = pyglet.text.Label(self.text, font_size=GUI.fontSize, font_name=GUI.font, anchor_x="center", anchor_y="center")



class BottomPanel:
	# At bottom of screen, handles multiple buttons, their drawing and position

	def __init__(self, width, height, color=GUI.panelColor, buttons=[]):
		self.color = color
		self.buttons = buttons
		self.leftButtons = []
		self.centerButtons = []
		self.rightButtons = []

		self.width = width
		self.height = height
		self.buttonWidth = height

		self.iconBatch = pyglet.graphics.Batch()

		for button in self.buttons:
			# Sort buttons into position groups
			if button.anchor == "left":
				self.leftButtons.append(button)
			elif button.anchor == "center":
				self.centerButtons.append(button)
			elif button.anchor == "right":
				self.rightButtons.append(button)
			# Add button icon sprite to batch
			button.sprite.batch = self.iconBatch
		
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
			button.y = 0
			button.width = self.buttonWidth
			button.height = self.height
			button.sprite.x = button.x + button.width/2
			button.sprite.y = button.y + button.height/2

		# Rebuild vertices
		vertices = []
		# Panel vertices
		vertices += Models.rect(0, 0, self.width, self.height)
		# Button vertices
		for button in self.buttons:
			vertices += Models.rect(button.x, button.y, button.x+button.width, button.y+button.height)
		self.panelModel = pyglet.graphics.vertex_list(4 * (len(self.buttons) + 1), ("v3f", vertices), "c4f")
		self.updateColors()


	def updateColors(self):
		colors = []
		# Panel colors
		colors += self.color * 4
		# Button colors
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
# Has a title and can hold buttons and text entry widgets

	def __init__(self, width, height, rightEdge, bottomEdge, title="", widgets=[], color=GUI.panelColor):
		self.width = width
		self.height = height
		self.rightEdge = rightEdge
		self.bottomEdge = bottomEdge

		self.widgets = widgets
		self.color = color

		self.iconBatch = pyglet.graphics.Batch()
		self.textBatch = pyglet.graphics.Batch()

		self.title = pyglet.text.Label(title, font_size=GUI.titleFontSize, font_name=GUI.font, anchor_x="left", anchor_y="center", batch=self.textBatch)
		self.titleHeight = GUI.titleFontSize * 1.5 + GUI.rightPanelMargin

		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					# Add button icon sprite to batch
					widget.sprite.batch = self.iconBatch

		self.layoutPanel()


	def layoutPanel(self):
		# Title position
		self.title.x = self.rightEdge - self.width + GUI.rightPanelMargin
		self.title.y = self.bottomEdge + self.height - (self.titleHeight-GUI.rightPanelMargin)/2 - GUI.rightPanelMargin

		# Widget location configuration
		for row in range(len(self.widgets)):
			widgetRow = self.widgets[row]
			for col in range(len(widgetRow)):
				widget = widgetRow[col]
				if type(widget) == Button:
					widget.x = self.rightEdge - self.width + GUI.rightPanelMargin*(col+1) + GUI.buttonSize*col
					widget.width = GUI.buttonSize
					widget.y = self.bottomEdge + self.height - self.titleHeight - GUI.rightPanelMargin*(row+1) - GUI.buttonSize*(row+1)
					widget.height = GUI.buttonSize
					widget.sprite.x = widget.x + widget.width/2
					widget.sprite.y = widget.y + widget.height/2

		# Rebuild vertices
		vertices = []
		# Panel vertices
		vertices += Models.rect(self.rightEdge-self.width, self.bottomEdge, self.rightEdge, self.bottomEdge+self.height)
		# Widget vertices
		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					vertices += Models.rect(widget.x, widget.y, widget.x+widget.width, widget.y+widget.height)
		self.panelModel = pyglet.graphics.vertex_list(len(vertices)//3, ("v3f", vertices), "c4f")
		self.updateColors()


	def updateColors(self):
		colors = []
		# Panel colors
		colors += self.color * 4
		# Button colors
		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					if widget.pressed:
						colors += widget.presscolor * 4
					elif widget.hovered:
						colors += widget.hovercolor * 4
					else:
						colors += widget.color * 4
		self.panelModel.colors = colors


	def draw(self):
		self.panelModel.draw(GL_QUADS)
		self.textBatch.draw()
		self.iconBatch.draw()


	def mouse_press(self, x, y):
		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					if widget.clicked(x, y):
						widget.pressed = True
						self.updateColors()
						return True
		return False

	def mouse_drag(self, x, y):
		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					if widget.clicked(x, y) and widget.pressed:
						widget.pressed = True
						self.updateColors()
					else:
						widget.pressed = False
						widget.hovered = False
						self.updateColors()

	def mouse_release(self, x, y):
		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					if widget.pressed:
						widget.pressed = False
						self.updateColors()
						widget.f()

	def mouse_motion(self, x, y):
		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					if widget.clicked(x, y):
						widget.hovered = True
						self.updateColors()
					else:
						widget.hovered = False
						self.updateColors()


if __name__ == '__main__':
	from Main import main
	main()