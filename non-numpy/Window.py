import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Environment import *
from Models import *
from GUI import *
from math import *

#================== TODO ==================#
# Change mouse cursor depending on operation
# Add Right panel and populate for the different modes (creature(s) selected / create / settings and sim stats)
# Finish building GUI
# 3D shading
# Implement batched rendering for creatures
# Add labels


class Window(pyglet.window.Window):
# main job is to draw the environment and allow the user to interact with it

	def __init__(self, environment):
		# Create window
		super(Window, self).__init__(caption="Life of Py", vsync=False, 
			config=Config(depth_size=24, double_buffer=True, sample_buffers=1, samples=2),
			resizable=True, fullscreen=False, width=1400, height=1000)

		# Load environment
		self.environment = environment

		# Mode
		self.mode = "2D"
		self.paused = False
		self.leftClickTool = None #"select", "drag", "panel"
		self.selectedCreatures = []

		# GUI
		self.playPauseButton = Button(anchor="left", icon=GUI.pauseIcon, f=self.playPause)
		self.slowerButton =    Button(anchor="left", icon=GUI.slowerIcon, f=self.slower)
		self.fasterButton =    Button(anchor="left", icon=GUI.fasterIcon, f=self.faster)
		self.createButton =    Button(anchor="center", icon=GUI.plusIcon, f=self.createMenu)
		self.settingsButton =  Button(anchor="center", icon=GUI.settingsIcon, f=self.settingsMenu)
		self.modeButton =      Button(anchor="right", icon=GUI.threeDIcon, f=self.switchMode)
		self.bottomPanel =     BottomPanel(width=self.width, height=80, buttons=[self.playPauseButton, self.slowerButton, self.fasterButton, self.createButton, self.settingsButton, self.modeButton])

		self.rightPanel = [] # Use a list since it might not always exist

		# Zooming parameters
		self.zoomLevel = 0.1
		self.zoomFactor = 1.5
		self.maxZoomIn = 0.01
		self.maxZoomOut = 10

		# Viewport positioning in world coordinates
		self.viewLeft   = self.zoomLevel * 0
		self.viewRight  = self.zoomLevel * self.width
		self.viewBottom = self.zoomLevel * 0
		self.viewTop    = self.zoomLevel * self.height
		self.viewWidth  = self.zoomLevel * self.width
		self.viewHeight = self.zoomLevel * self.height

		# For bounding
		self.xmin = 0
		self.xmax = self.width
		self.ymin = 0
		self.ymax = self.height

		# 3D stuff (x,y are plane of movement, z is up)
		center = self.environment.gridSize * self.environment.cellSize / 2
		self.playerPosition = Vector(center,center,5)
		self.playerVelocity = Vector(0,0,0)
		self.playerSpeed = 20
		self.playerLook = (-45, 90) # (xy rotation, z rotation)
		self.playerMove = Vector(0,0,0)
		self.mouseSensitivity = 0.2
		self.FOV = 75

		self.loadEnvironmentModels()
		self.loadCreatureModels()


		# OpenGL setup
		glClearColor(0, 0, 0, 0)
		glEnable(GL_DEPTH_TEST)
		#glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		#glEnable(GL_LINE_SMOOTH)
		#glEnable(GL_POLYGON_SMOOTH)
		#glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
		#glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
		#self.initShading()
		#self.initFog()
		#glLineWidth(4)

		# Runtime things
		self.set_exclusive_mouse(False)
		self.FPS = pyglet.clock.ClockDisplay(color=(0.5, 0.5, 0.5, 0.5))
		self.FPS.label.y = self.height-50
		self.timeFactor = 1
		self.minTimeFactor = 1/4
		self.maxTimeFactor = 16

	def initFog(self):
		glEnable(GL_FOG)
		glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0, 0, 0, 1))
		glHint(GL_FOG_HINT, GL_DONT_CARE)
		glFogi(GL_FOG_MODE, GL_LINEAR)
		glFogf(GL_FOG_START, 500)
		glFogf(GL_FOG_END, 1000)

	def initShading(self):
		glShadeModel(GL_FLAT)
		#glEnable(GL_CULL_FACE)
		#glEnable(GL_LIGHTING)
		#glEnable(GL_LIGHT0)
		#glEnable(GL_LIGHT1)

	def start(self):
		pyglet.clock.schedule(self.update)
		pyglet.app.run()

	def update(self, dt):
		# Main app non-input event loop
		if not self.paused:
			self.environment.update(self.timeFactor*dt)
		if self.mode == "3D":
			self.playerVelocity.x = self.playerSpeed * cos(radians(self.playerLook[0]) + atan2(self.playerMove.y, self.playerMove.x)) * bool(self.playerMove.x or self.playerMove.y)
			self.playerVelocity.y = self.playerSpeed * sin(radians(self.playerLook[0]) + atan2(self.playerMove.y, self.playerMove.x)) * bool(self.playerMove.x or self.playerMove.y)
			self.playerVelocity.z = self.playerSpeed * self.playerMove.z
			self.playerVelocity = self.playerSpeed * unit(self.playerVelocity)
			self.playerPosition += self.playerVelocity * dt


#================== MOUSE EVENTS ==================#

	def on_mouse_press(self, x, y, button, modifiers):
		if self.mode == "2D":
			if button == mouse.LEFT:
				# GUI stuff
				# Right panel clicking
				for panel in self.rightPanel:
					if x < panel.rightEdge - panel.width:
						self.rightPanel = []
					else:
						if panel.mouse_press(x, y):
							self.leftClickTool = "panel"
							return
				# Bottom panel clicking
				if self.bottomPanel.mouse_press(x, y):
					self.leftClickTool = "panel"
					return
				# Check for click on creature
				worldX, worldY = self.mouseToWorld(x,y)
				for herd in self.environment.herds:
					for creature in herd.creatures:
						# Creature clicked
						if (creature.pos.x - creature.size <= worldX <= creature.pos.x + creature.size and
							creature.pos.y - creature.size <= worldY <= creature.pos.y + creature.size):
							# If part of the selection is clicked, start to drag
							if creature in self.selectedCreatures:
								self.leftClickTool = "drag"
								return
							# If creature not in selection clicked, clear current selection and select new creature
							else:
								self.selectedCreatures = [creature]
								self.leftClickTool = "drag"
								return
				# Nothing was clicked, deselect everything
				self.selectedCreatures = []
				self.leftClickTool = None


	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		if self.mode == "2D":
			if buttons & mouse.LEFT:
				# Start a box selection
				if self.leftClickTool == None:
					self.leftClickTool = "select"
					self.selectionStartX, self.selectionStartY = self.mouseToWorld(x,y)
					self.selectionEndX, self.selectionEndY = self.mouseToWorld(x,y)
				# In the process of a selection
				elif self.leftClickTool == "select":
					self.selectionEndX, self.selectionEndY = self.mouseToWorld(x,y)
					self.selectedCreatures = []
					for herd in self.environment.herds:
						for creature in herd.creatures:
							if ((self.selectionStartX <= creature.pos.x <= self.selectionEndX or
								self.selectionEndX <= creature.pos.x <= self.selectionStartX) and
								(self.selectionStartY <= creature.pos.y <= self.selectionEndY or
								self.selectionEndY <= creature.pos.y <= self.selectionStartY)):
								self.selectedCreatures.append(creature)
				# In the process of dragging
				elif self.leftClickTool == "drag":
					for creature in self.selectedCreatures:
						creature.pos.x += dx * self.zoomLevel
						creature.pos.y += dy * self.zoomLevel
						creature.vel = Vector(0,0,0)
				# GUI stuff
				elif self.leftClickTool == "panel":
					self.bottomPanel.mouse_drag(x,y)
					for panel in self.rightPanel:
						panel.mouse_drag(x,y)

			elif buttons & mouse.RIGHT:
				# Panning the view
				self.viewLeft   -= dx * self.zoomLevel
				self.viewRight  -= dx * self.zoomLevel
				self.viewBottom -= dy * self.zoomLevel
				self.viewTop    -= dy * self.zoomLevel

		elif self.mode == "3D":
			self.playerLook = (self.playerLook[0] - dx * self.mouseSensitivity,
				max(0, min(180, self.playerLook[1] + dy * self.mouseSensitivity)))


	def on_mouse_release(self, x, y, button, modifiers):
		if self.mode == "2D":
			if button == mouse.LEFT:
				if self.leftClickTool == "panel":
					self.bottomPanel.mouse_release(x, y)
					for panel in self.rightPanel:
						panel.mouse_release(x,y)

				elif self.leftClickTool == "select":
					self.leftClickTool = "drag"
				elif self.leftClickTool == "drag":
					pass
				else:
					self.leftClickTool = None


	def on_mouse_motion(self, x, y, dx, dy):
		if self.mode == "3D":
			self.playerLook = (self.playerLook[0] - dx * self.mouseSensitivity,
				max(0, min(180, self.playerLook[1] + dy * self.mouseSensitivity)))
		
		elif self.mode == "2D":
			self.bottomPanel.mouse_motion(x, y)
			for panel in self.rightPanel:
				panel.mouse_motion(x,y)


	def on_mouse_scroll(self, x, y, dx, dy):
		if self.mode == "2D":
			# Get scale factor
			f = self.zoomFactor**(-dy)
			# If zoomLevel is in the proper range
			if self.maxZoomIn < self.zoomLevel * f < self.maxZoomOut:
				self.zoomLevel *= f

				worldX, worldY = self.mouseToWorld(x,y)

				self.viewWidth *= f
				self.viewHeight *= f

				self.viewLeft   = worldX - x * (self.viewWidth / self.width)
				self.viewRight  = worldX - x * (self.viewWidth / self.width) + self.viewWidth
				self.viewBottom = worldY - y * (self.viewHeight / self.height)
				self.viewTop    = worldY - y * (self.viewHeight / self.height) + self.viewHeight
		elif self.mode == "3D":
			self.FOV *= self.zoomFactor**(-dy)
			self.mouseSensitivity *= self.zoomFactor**(-dy)


	def mouseToWorld(self, mouseX, mouseY):
		worldX = self.viewLeft   + mouseX * (self.viewWidth  / self.width)
		worldY = self.viewBottom + mouseY * (self.viewHeight / self.height)
		return worldX, worldY


	def on_resize(self, width, height):
		# Update the 2D viewport
		glViewport(0, 0, width, height)
		viewWidthChange = width * self.zoomLevel - self.viewWidth
		self.viewWidth += viewWidthChange
		self.viewLeft -= viewWidthChange/2
		self.viewRight += viewWidthChange/2
		viewHeightChange = height * self.zoomLevel - self.viewHeight
		self.viewHeight += viewHeightChange
		self.viewBottom -= viewHeightChange/2
		self.viewTop += viewHeightChange/2

		# Update the bottom panel
		self.bottomPanel.width = width
		self.bottomPanel.layoutPanel()

		# Update the right panel
		for panel in self.rightPanel:
			panel.width = GUI.rightPanelWidth
			panel.height = height-self.bottomPanel.height
			panel.rightEdge = width
			panel.bottomEdge = self.bottomPanel.height
			panel.layoutPanel()

		# Update FPS display
		self.FPS.label.y = self.height - 50


#================== KEYBOARD EVENTS ==================#

	def on_key_press(self, symbol, modifiers):
		if self.mode == "3D":
			if symbol == key.ESCAPE:
				self.switchMode()
			if symbol == key.W:
				self.playerMove.y += 1
			elif symbol == key.A:
				self.playerMove.x -= 1
			elif symbol == key.S:
				self.playerMove.y -= 1
			elif symbol == key.D:
				self.playerMove.x += 1
			elif symbol == key.SPACE:
				self.playerMove.z += 1
			elif symbol == key.LSHIFT:
				self.playerMove.z -= 1

	def on_key_release(self, symbol, modifiers):
		if self.mode == "3D":
			if symbol == key.W:
				self.playerMove.y -= 1
			elif symbol == key.A:
				self.playerMove.x += 1
			elif symbol == key.S:
				self.playerMove.y += 1
			elif symbol == key.D:
				self.playerMove.x -= 1
			elif symbol == key.SPACE:
				self.playerMove.z -= 1
			elif symbol == key.LSHIFT:
				self.playerMove.z += 1


#================== BUTTON FUNCTIONS ==================#

	def playPause(self):
		if self.paused:
			self.paused = False
			self.playPauseButton.sprite.image = GUI.pauseIcon
		else:
			self.paused = True
			self.playPauseButton.sprite.image = GUI.playIcon

	def slower(self):
		if self.timeFactor > self.minTimeFactor:
			self.timeFactor /= 2

	def faster(self):
		if self.timeFactor < self.maxTimeFactor:
			self.timeFactor *= 2

	def switchMode(self):
		if self.mode == "2D":
			self.mode = "3D"
			self.set_exclusive_mouse(True)
			self.playerMove = Vector(0,0,0)
			self.loadEnvironmentModels()

		elif self.mode == "3D":
			self.mode = "2D"
			self.set_exclusive_mouse(False)
			self.playerMove = Vector(0,0,0)
			self.loadEnvironmentModels()

	def addSomeCreatures(self):
		self.environment.createHerd(20)
		self.loadCreatureModels()

	def createMenu(self):
		creatureButton = Button(icon=GUI.creatureIcon, text="Creature", f=self.addSomeCreatures)
		treeButton = Button(icon=GUI.treeIcon, text="Tree", f=self.addSomeCreatures)
		createPanel = RightPanel(width=GUI.rightPanelWidth, height=self.height-self.bottomPanel.height, rightEdge=self.width, bottomEdge=self.bottomPanel.height, title="Create", widgets=[[creatureButton, treeButton]])
		self.rightPanel.append(createPanel)

	def settingsMenu(self):
		settingsPanel = RightPanel(width=GUI.rightPanelWidth, height=self.height-self.bottomPanel.height, rightEdge=self.width, bottomEdge=self.bottomPanel.height, title="Settings", widgets=[])
		self.rightPanel.append(settingsPanel)

#================== MODELS ==================#

	def loadEnvironmentModels(self):
		# Must be called to load all of the 2D/3D models into memory
		self.environmentBatch = pyglet.graphics.Batch()

		# Terrain
		terrainVertices, terrainColors = Models.terrain(self.environment.terrainResolution, 
			self.environment.cellSize/(self.environment.terrainResolution//self.environment.gridSize), self.environment.land)
		if self.mode == "2D":
			# Depth test hack for terrain
			for c in range(len(terrainVertices)):
				if (c+1) % 3 == 0:
					terrainVertices[c] -= terrainVertices[c-1]
		self.environmentBatch.add(len(terrainVertices)//3, GL_QUADS, None, ("v3f/static", terrainVertices), ("c3f/static", terrainColors))

		# Trees
		for tree in self.environment.trees:
			treeVertices, treeColors = Models.tree(tree)
			if self.mode == "2D":
				group = None
				treeVertices = self.depthHack(treeVertices, tree.y)
			elif self.mode == "3D":
				group = BillboardGroup(tree.x, tree.y, self)
				treeVertices = self.rotateUp(treeVertices, tree.y)
			tree.model = self.environmentBatch.add(len(treeVertices)//3, GL_QUADS, group, ("v3f/static", treeVertices), ("c3f/static", treeColors))

		# Shrubs
		for shrub in self.environment.shrubs:
			shrubVertices, shrubColors = Models.shrub(shrub)
			if self.mode == "2D":
				group = None
				shrubVertices = self.depthHack(shrubVertices, shrub.y)
			elif self.mode == "3D":
				group = BillboardGroup(shrub.x, shrub.y, self)
				shrubVertices = self.rotateUp(shrubVertices, shrub.y)
			shrub.model = self.environmentBatch.add(len(shrubVertices)//3, GL_QUADS, group, ("v3f/static", shrubVertices), ("c3f/static", shrubColors))

		# Rocks
		for rock in self.environment.rocks:
			rockVertices = Models.blob(rock.x, rock.y, rock.n, rock.r)
			rockColors = rock.color*4*rock.n
			if self.mode == "2D":
				group = None
				rockVertices = self.depthHack(rockVertices, rock.y)
			elif self.mode == "3D":
				group = BillboardGroup(rock.x, rock.y, self)
				rockVertices = self.rotateUp(rockVertices, rock.y)
			rock.model = self.environmentBatch.add(len(rockVertices)//3, GL_QUADS, group, ("v3f/static", rockVertices), ("c3f/static", rockColors))


	def depthHack(self, vertices, y):
		# Depth test hack, uses 2.5D
		# Loop through z coordinates
		for c in range(2,len(vertices),3):
			vertices[c] -= y
		return vertices


	def rotateUp(self, vertices, y):
		# For 3D mode, rotate entities up 90 degrees off the plane
		# Loop through y coordinates
		for c in range(1,len(vertices),3):
			# Copy y to z
			vertices[c+1] = vertices[c] - y
			# Flatten on y axis to y value passed in
			vertices[c] = y
		return vertices


	def loadCreatureModels(self):
		self.creatureBatch = pyglet.graphics.Batch()
		for herd in self.environment.herds:
			for creature in herd.creatures:
				creatureVertices, creatureColors = Models.creature(creature)
				creature.model = self.creatureBatch.add(len(creatureVertices)//3, 
					GL_QUADS, None, ("v3f/dynamic", creatureVertices), ("c3f/static", creatureColors))


#================== DRAWING ==================#

	def on_draw(self):
		self.clear()
		if self.mode == "2D":
			self.setup2D()
		elif self.mode == "3D":
			self.setup3D()
		self.environmentBatch.draw()
		#self.creatureBatch.draw()
		self.drawCreatures()
		self.drawSelectionBox()
		self.setupGUI()
		self.drawGUI()


	def setup2D(self):
		# Initialize Projection matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		# Initialize Modelview matrix
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		# Set orthographic projection
		glOrtho(self.viewLeft, self.viewRight, self.viewBottom, self.viewTop, -100, 100000)
		# Set background color
		glClearColor(0, 0, 0, 0)


	def setup3D(self):
		# Initialize Projection matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		# Initialize Modelview matrix
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		# Set the perspective projection
		gluPerspective(self.FOV, self.width/self.height, 1, 1000)
		# XY rotation
		glRotatef(-self.playerLook[0], 0, 0, 1)
		# Z rotation
		glRotatef(-self.playerLook[1], 
			cos(radians(self.playerLook[0])), 
			sin(radians(self.playerLook[0])), 
			0)
		# Translate from player position (move the world, not the camera)
		glTranslatef(-self.playerPosition.x, -self.playerPosition.y, -self.playerPosition.z)
		# Set background color
		glClearColor(0, 191/255, 1, 1)


	def setupGUI(self):
		# Initialize Projection matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self.width, 0, self.height, -1, 1)
		# Initialize Modelview matrix
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()


	def drawGUI(self):
		# Drawing
		glEnable(GL_BLEND)
		glDisable(GL_DEPTH_TEST)
		# Draw FPS display
		self.FPS.draw()
		# Draw UI controls
		if self.mode == "2D":
			self.bottomPanel.draw()
			for panel in self.rightPanel:
				panel.draw()
		glDisable(GL_BLEND)
		glEnable(GL_DEPTH_TEST)


	def drawSelectionBox(self):
		# Draw mouse selection box
		if self.leftClickTool == "select":
			glEnable(GL_BLEND)
			glDisable(GL_DEPTH_TEST)
			glColor4f(1,1,1,0.3)
			vertices = Models.rect(self.selectionStartX, self.selectionStartY, self.selectionEndX, self.selectionEndY)
			pyglet.graphics.vertex_list(len(vertices)//3, ("v3f/static", vertices)).draw(GL_QUADS)
			glDisable(GL_BLEND)
			glEnable(GL_DEPTH_TEST)


	def drawCreatures(self):
		for herd in self.environment.herds:
			# Draw the center of mass
			self.drawSquare(herd.getCenter(), 3, color=(1,0,0,1))
			for creature in herd.creatures:
				glPushMatrix()
				glColor4f(1,1,1,1)
				if self.mode == "3D":
					self.rotateBillboard(creature.pos)
					glTranslatef(creature.pos.x, creature.pos.y, 0)
				else:
					glTranslatef(creature.pos.x, creature.pos.y, -creature.pos.y)
				creature.model.draw(GL_QUADS)
				glPopMatrix()
		for creature in self.selectedCreatures:
			glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
			self.drawSquare(creature.pos, creature.size, color=(1,0,0,1))
			glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


	def rotateBillboard(self, pos):
		# Rotate the billboard frame up 90 and towards the player
		glTranslatef(pos.x, pos.y, 0)
		glRotatef(90,1,0,0)
		faceAngle = 90-degrees(atan2(self.playerPosition.y - pos.y, self.playerPosition.x - pos.x))
		glRotatef(faceAngle,0,-1,0)
		glTranslatef(-pos.x, -pos.y, 0)


	def drawSquare(self, pos, size, color):
		glPushMatrix()
		glTranslatef(pos.x, pos.y, -pos.y)
		# Get square data and draw
		glColor4f(*color)
		pyglet.graphics.vertex_list(4, ("v3f/static", Models.centeredSquare(size))).draw(GL_QUADS)
		glPopMatrix()


class BillboardGroup(pyglet.graphics.Group):
# For static billboard objects

	def __init__(self, x, y, window, parent=None):
		self.x = x
		self.y = y
		self.window = window
		super().__init__(parent)

	def set_state(self):
		glPushMatrix()
		glTranslatef(self.x, self.y, 0)
		faceAngle = 90-degrees(atan2(self.window.playerPosition.y - self.y, self.window.playerPosition.x - self.x))
		glRotatef(faceAngle, 0,0,-1)
		glTranslatef(-self.x, -self.y, 0)
		pass

	def unset_state(self):
		if self.window.mode == "3D":
			glPopMatrix()
			pass


if __name__ == '__main__':
	from Main import main
	main()