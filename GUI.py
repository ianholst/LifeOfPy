import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Models import *


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
	heartIcon = pyglet.resource.image("heart.png")
	creatureIcon = pyglet.resource.image("creature.png")
	treeIcon = pyglet.resource.image("tree.png")
	copyIcon = pyglet.resource.image("copy.png")
	killIcon = pyglet.resource.image("kill.png")

	for icon in [killIcon,copyIcon,heartIcon,playIcon,pauseIcon,slowerIcon,fasterIcon,noIcon,threeDIcon,plusIcon,settingsIcon,creatureIcon,treeIcon]:
		icon.anchor_x = icon.width/2
		icon.anchor_y = icon.height/2

	# Colors
	panelColor = (0.05,0.05,0.05,0.8)
	rightPanelColor = (0.05,0.05,0.05,0.9)
	buttonColor = (0,0,0,0)
	buttonHoverColor = (1,1,1,0.1)
	buttonPressColor = (1,1,1,0.5)
	textBoxColor = (1,1,1,0.1)

	# Fonts
	font = "Calibri"
	fontSize = 16
	titleFontSize = 30

	# Panels
	buttonSize = 80
	bottomPanelHeight = 80
	rightPanelWidth = 400
	rightPanelMargin = 20
	titleHeight = titleFontSize * 2
	labelWidth = 150
	textPad = 5


class BottomPanel:
	# At bottom of screen, handles multiple buttons, their drawing and position

	def __init__(self, width, height, batch, color=GUI.panelColor, buttons=[]):
		self.color = color
		self.buttons = buttons
		self.leftButtons = []
		self.centerButtons = []
		self.rightButtons = []

		self.width = width
		self.height = height
		self.buttonWidth = height

		self.batch = batch

		for button in self.buttons:
			# Sort buttons into position groups
			if button.anchor == "left":
				self.leftButtons.append(button)
			elif button.anchor == "center":
				self.centerButtons.append(button)
			elif button.anchor == "right":
				self.rightButtons.append(button)
			# Add button icon sprite to batch
			button.sprite.batch = self.batch
		
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
		self.batch.draw()

	def on_mouse_press(self, x, y):
		if y < self.height:
			for button in self.buttons:
				if button.clickTest(x, y):
					button.pressed = True
					self.updateColors()
					return True
		return False

	def on_mouse_drag(self, x, y):
		for button in self.buttons:
			if button.clickTest(x, y) and button.pressed:
				button.pressed = True
				self.updateColors()
			else:
				button.pressed = False
				button.hovered = False
				self.updateColors()

	def on_mouse_release(self, x, y):
		if y < self.height:
			for button in self.buttons:
				if button.pressed:
					button.pressed = False
					self.updateColors()
					button.f()

	def on_mouse_motion(self, x, y):
		for button in self.buttons:
			if button.clickTest(x, y):
				button.hovered = True
				self.updateColors()
			else:
				button.hovered = False
				self.updateColors()


class Button:
	# Button class that is placed on a panel, reacts to mouse events, and calls a function when pressed

	def __init__(self, batch, anchor="left", f=None, icon=GUI.noIcon, text="", color=GUI.buttonColor, hovercolor=GUI.buttonHoverColor, presscolor=GUI.buttonPressColor):
		self.anchor = anchor # left, center, or right
		self.f = f
		self.sprite = pyglet.sprite.Sprite(icon)
		self.sprite.batch = batch
		self.pressed = False
		self.hovered = False
		self.width = GUI.buttonSize
		self.height = GUI.buttonSize

		self.text = text
		if self.text != "":
			self.label = pyglet.text.Label(self.text, font_size=GUI.fontSize, font_name=GUI.font, anchor_x="center", anchor_y="center", batch=batch)

		self.color = color
		self.hovercolor = hovercolor
		self.presscolor = presscolor


	def clickTest(self, x, y):
		return (self.x < x < self.x + self.width and
				self.y < y < self.y + self.height)



class Indicator:
	# Labeled indicator that displays properties as they change

	def __init__(self, label, value, batch):
		self.label = pyglet.text.Label(label, font_size=GUI.fontSize, font_name=GUI.font, anchor_x="left", anchor_y="center", batch=batch)
		self.value = pyglet.text.Label(value, font_size=GUI.fontSize, font_name=GUI.font, anchor_x="left", anchor_y="center", batch=batch)


class PropertyEditor:
	# Labeled text box that allows the user to change values of variables
	# Based off code from official pyglet tutorials

	def __init__(self, label, value, batch):
		self.label = pyglet.text.Label(label, font_size=GUI.fontSize, font_name=GUI.font, anchor_x="left", anchor_y="center", batch=batch)
		self.document = pyglet.text.document.UnformattedDocument(value)
		self.document.set_style(0, len(self.document.text), dict(color=(255,255,255,255), font_size=GUI.fontSize, font_name=GUI.font,))
		self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, 0, 0, multiline=False, batch=batch)
		self.caret = pyglet.text.caret.Caret(self.layout, color=(255,255,255), batch=batch)

	def clickTest(self, x, y):
		return (self.layout.x-GUI.textPad < x < self.layout.x+self.layout.width+GUI.textPad and
				self.layout.y-GUI.textPad < y < self.layout.y+self.layout.height+GUI.textPad)


class RightPanel:
# Has a title and can hold buttons, labels, and text entry widgets

	def __init__(self, width, height, rightEdge, bottomEdge, batch, window, title="", widgets=[], color=GUI.rightPanelColor):
		self.width = width
		self.height = height
		self.rightEdge = rightEdge
		self.bottomEdge = bottomEdge
		self.widgets = widgets
		self.color = color
		self.batch = batch
		self.window = window
		self.title = pyglet.text.Label(title, font_size=GUI.titleFontSize, font_name=GUI.font, anchor_x="left", anchor_y="center", batch=self.batch)

		self.focus = None
		self.textCursor = self.window.get_system_mouse_cursor("text")

		self.layoutPanel()
		self.focusOn(None)


	def layoutPanel(self):
		# Title position
		self.title.x = self.rightEdge - self.width + GUI.rightPanelMargin
		self.title.y = self.bottomEdge + self.height - GUI.titleHeight/2

		# Widget location configuration
		y = self.bottomEdge + self.height - GUI.titleHeight
		for row in range(len(self.widgets)):
			widgetRow = self.widgets[row]
			# Dynamic row height, y is the bottom coordinate of the current row
			if type(widgetRow[0]) == Button:
				y -= GUI.rightPanelMargin + GUI.buttonSize
			elif type(widgetRow[0]) == PropertyEditor:
				font = widgetRow[0].document.get_font()
				height = font.ascent - font.descent
				y -= GUI.rightPanelMargin + 2*GUI.textPad + height
			elif type(widgetRow[0]) == Indicator:
				font = widgetRow[0].label.document.get_font()
				height = font.ascent - font.descent
				y -= GUI.rightPanelMargin + 2*GUI.textPad + height

			# Lay out the individual widget positions
			for col in range(len(widgetRow)):
				widget = widgetRow[col]

				if type(widget) == Button:
					widget.x = self.rightEdge - self.width + GUI.rightPanelMargin*(col+1) + GUI.buttonSize*col
					widget.y = y
					if widget.text == "":
						widget.sprite.x = widget.x + widget.width/2
						widget.sprite.y = widget.y + widget.height/2
					else:
						widget.sprite.x = widget.x + widget.width/2
						widget.sprite.y = widget.y + widget.height*2/3
						widget.label.x = widget.x + widget.width/2
						widget.label.y = widget.y + widget.height/4

				elif type(widget) == PropertyEditor:
					widget.label.x = self.rightEdge - self.width + GUI.rightPanelMargin
					widget.label.y = y + GUI.textPad + height/2
					widget.layout.width = self.width - 2*GUI.rightPanelMargin - GUI.labelWidth
					widget.layout.height = height
					widget.layout.x = self.rightEdge - self.width + GUI.rightPanelMargin + GUI.labelWidth
					widget.layout.y = y + GUI.textPad

				elif type(widget) == Indicator:
					widget.label.x = self.rightEdge - self.width + GUI.rightPanelMargin
					widget.label.y = y + GUI.textPad + height/2
					widget.value.x = self.rightEdge - self.width + GUI.rightPanelMargin + GUI.labelWidth
					widget.value.y = y + GUI.textPad + height/2


		# Rebuild vertices
		vertices = []
		# Panel vertices
		vertices += Models.rect(self.rightEdge-self.width, self.bottomEdge, self.rightEdge, self.bottomEdge+self.height)
		# Widget vertices
		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					vertices += Models.rect(widget.x, widget.y, widget.x+widget.width, widget.y+widget.height)
				elif type(widget) == PropertyEditor:
					vertices += Models.rect(widget.layout.x-GUI.textPad, widget.layout.y-GUI.textPad, widget.layout.x+widget.layout.width+GUI.textPad, widget.layout.y+widget.layout.height+GUI.textPad)
				elif type(widget) == Indicator:
					pass
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
				elif type(widget) == PropertyEditor:
					colors += GUI.textBoxColor * 4
				elif type(widget) == Indicator:
					pass

		self.panelModel.colors = colors


	def draw(self):
		self.panelModel.draw(GL_QUADS)
		self.batch.draw()

	def focusOn(self, widget):
		# Remove focus from any widget already focused on
		if self.focus != None:
			self.focus.caret.visible = False
			self.focus.caret.mark = self.focus.caret.position = 0

		self.focus = widget
		# If an actual widget has been passed in
		if self.focus != None:
			self.focus.caret.visible = True
			self.focus.caret.mark = 0
			self.focus.caret.position = len(self.focus.document.text)
		# Deselect all widgets
		else:
			for row in self.widgets:
				for widget in row:
					if type(widget) == PropertyEditor:
						widget.caret.visible = False
						widget.caret.mark = widget.caret.position = 0




	# Mouse interactions based off code from official pyglet tutorials
	def on_mouse_press(self, x, y):
		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					if widget.clickTest(x, y):
						widget.pressed = True
						self.updateColors()
						return True
				elif type(widget) == PropertyEditor:
					if widget.clickTest(x, y):
						self.focusOn(widget)
						self.focus.caret.on_mouse_press(x, y, 0, 0)
						return True
				elif type(widget) == Indicator:
					pass
		self.focusOn(None)
		return False

	def on_mouse_drag(self, x, y):
		if self.focus != None:
			self.focus.caret.on_mouse_drag(x, y, 0, 0, 0, 0)
		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					if widget.clickTest(x, y) and widget.pressed:
						widget.pressed = True
						self.updateColors()
					else:
						widget.pressed = False
						widget.hovered = False
						self.updateColors()
				elif type(widget) == PropertyEditor:
					pass
				elif type(widget) == Indicator:
					pass

	def on_mouse_release(self, x, y):
		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					if widget.pressed:
						widget.pressed = False
						self.updateColors()
						widget.f()
				elif type(widget) == PropertyEditor:
					pass
				elif type(widget) == Indicator:
					pass

	def on_mouse_motion(self, x, y):
		onText = False
		for row in self.widgets:
			for widget in row:
				if type(widget) == Button:
					if widget.clickTest(x, y):
						widget.hovered = True
						self.updateColors()
					else:
						widget.hovered = False
						self.updateColors()
				elif type(widget) == PropertyEditor:
					if widget.clickTest(x, y):
						self.window.set_mouse_cursor(self.textCursor)
						onText = True
				elif type(widget) == Indicator:
					pass
		if not onText:
			self.window.set_mouse_cursor(None)

	def on_text(self, text):
		if self.focus != None:
			self.focus.caret.on_text(text)

	def on_text_motion(self, motion):
		if self.focus != None:
			self.focus.caret.on_text_motion(motion)
	  
	def on_text_motion_select(self, motion):
		if self.focus != None:
			self.focus.caret.on_text_motion_select(motion)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.ESCAPE:
			# Delete self
			self.window.rightPanel = []
		# Submit contents when enter pressed
		elif self.focus != None and symbol == key.ENTER:
			# Submit
			try:
				self.window.changeProperty(self.focus, eval(self.focus.document.text))
			except NameError:
				self.window.changeProperty(self.focus, self.focus.document.text)
			except SyntaxError:
				self.focus.document.text = "INVALID"
			# Deselect
			self.focusOn(None)



if __name__ == '__main__':
	from Main import main
	main()