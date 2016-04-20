import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Herd import *
from Environment import *
from Models import *
from GUI import *
from math import *

# ================ TODO================
# * Change mouse cursor depending on operation
# * Add Right panel and populate for the different modes (creature(s) selected / create / settings and sim stats)
# * Finish building GUI
# * 3D shading
# * Implement batched rendering for creatures
# * Make left click select and right click pan
# * Add labels


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
		self.bottomPanel = BottomPanel(width=self.width, height=100)
		
		self.playPauseButton = Button(self.bottomPanel, anchor="left", icon=GUI.pauseIcon, f=self.playPause)
		self.slowerButton =    Button(self.bottomPanel, anchor="left", icon=GUI.slowerIcon, f=self.slower)
		self.fasterButton =    Button(self.bottomPanel, anchor="left", icon=GUI.fasterIcon, f=self.faster)

		Button(self.bottomPanel, anchor="center", text="Add creatures", icon=GUI.plusIcon, f=lambda:self.environment.createHerd(20))

		Button(self.bottomPanel, anchor="right", text="3D", icon=GUI.threeDIcon, f=self.switchMode)
		#Button(self.bottomPanel, anchor="right", text="woo", icon=GUI.noIcon, f=self.change)

		# Viewport positioning in world coordinates
		self.viewLeft = 0
		self.viewRight = self.width
		self.viewBottom = 0
		self.viewTop = self.height
		self.viewWidth = self.width
		self.viewHeight = self.height

		# Zooming behaviors
		self.zoomLevel = 1
		self.zoomFactor = 1.5
		self.maxZoomIn = 0.1
		self.maxZoomOut = 10

		# For bounding
		self.xmin = 0
		self.xmax = self.width
		self.ymin = 0
		self.ymax = self.height

		# 3D stuff (x,y are plane of movement, z is up)
		self.playerPosition = Vector(0,0,10)
		self.playerVelocity = Vector(0,0,0)
		self.playerSpeed = 1000
		self.playerLook = (0, 90) # (xy rotation, z rotation)
		self.playerMove = Vector(0,0,0)
		self.mouseSensitivity = 0.2
		self.FOV = 70

		self.loadEnvironmentModels()


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
			self.playerPosition += self.playerVelocity * dt


#================== MOUSE EVENTS ==================#

	def on_mouse_press(self, x, y, button, modifiers):
		if self.mode == "2D":
			if button == mouse.LEFT:
				# GUI stuff
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
							# Get rid of current selection
							if creature in self.selectedCreatures:
								self.leftClickTool = "drag"
								return
							else:
								self.selectedCreatures = [creature]
								self.leftClickTool = "drag"
								return
				# Nothing was clicked, deselect
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
		# TODO: fix this to take into account zoom level
		glViewport(0, 0, width, height)
		dViewWidth = width * self.zoomLevel - self.viewWidth
		self.viewWidth += dViewWidth
		self.viewLeft -= dViewWidth/2
		self.viewRight += dViewWidth/2

		dViewHeight = height * self.zoomLevel - self.viewHeight
		self.viewHeight += dViewHeight
		self.viewBottom -= dViewHeight/2
		self.viewTop += dViewHeight/2

		# Update the bottom panel
		self.bottomPanel.width = width
		self.bottomPanel.layoutPanel()
		# Update FPS display
		self.FPS.label.y = self.height-50


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
		self.timeFactor -= 1

	def faster(self):
		self.timeFactor += 1

	def switchMode(self):
		# Will eventually have to be more active
		if self.mode == "2D":
			self.mode = "3D"
			self.set_exclusive_mouse(True)
			self.playerMove = Vector(0,0,0)

			for tree in self.environment.trees:
				for c in range(2292):
					if (c+1) % 3 == 0:
						tree.model.vertices[c] += tree.y


		elif self.mode == "3D":
			self.mode = "2D"
			self.set_exclusive_mouse(False)
			self.playerMove = Vector(0,0,0)

			for tree in self.environment.trees:
				for c in range(2292):
					if (c+1) % 3 == 0:
						tree.model.vertices[c] -= tree.y

#================== MODELS ==================#

	def loadEnvironmentModels(self):
		# Separate into 2D and 3D
		# Terrain
		self.terrainBatch = pyglet.graphics.Batch()
		terrainVertices, terrainColors = Models.terrain(self.environment.gridSize, self.environment.cellSize, self.environment.land)
		self.terrainBatch.add(len(terrainVertices)//3, GL_QUADS, None, ("v3f/static", terrainVertices), ("c3f/static", terrainColors))
		# Trees
		self.treeBatch = pyglet.graphics.Batch()
		for tree in self.environment.trees:
			treeVertices, treeColors = Models.tree(tree)
			if self.mode == "3D":
				group = BillboardGroup(Vector(tree.x, tree.y, 0), self)
			elif self.mode == "2D":
				group = None
				# Depth test hack
				for c in range(len(treeVertices)):
					if (c+1) % 3 == 0:
						treeVertices[c] -= tree.y

			tree.model = self.treeBatch.add(len(treeVertices)//3, GL_QUADS, group, ("v3f/static", treeVertices), ("c3f/static", treeColors))
		# Shrubs

		# Rocks

	def loadCreatureModel(self):
		pass

#================== DRAWING ==================#

	def on_draw(self):
		self.clear()
		if self.mode == "2D":
			self.drawEnvironment2D()
		elif self.mode == "3D":
			self.drawEnvironment3D()
		self.drawUI()

#================== 2D DRAWING ==================#

	def drawEnvironment2D(self):
		# Initialize Projection matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		# Initialize Modelview matrix
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		# Set orthographic projection
		glOrtho(self.viewLeft, self.viewRight, self.viewBottom, self.viewTop, -10000, 10000)

		# Drawing
		self.terrainBatch.draw()
		self.treeBatch.draw()
		self.drawCenterOfMass()
		self.drawCreatures()
		self.drawSelector()


#================== 3D DRAWING ==================#

	def drawEnvironment3D(self):
		# Initialize Projection matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		# Initialize Modelview matrix
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		# Set the perspective projection
		gluPerspective(self.FOV, self.width/self.height, 1, 10000)

		# XY rotation
		glRotatef(-self.playerLook[0], 0, 0, 1)
		# Z rotation
		glRotatef(-self.playerLook[1], 
			cos(radians(self.playerLook[0])), 
			sin(radians(self.playerLook[0])), 
			0)
		# Translate from player position (move the world, not the camera)
		glTranslatef(-self.playerPosition.x, -self.playerPosition.y, -self.playerPosition.z)

		# Drawing
		self.terrainBatch.draw()
		self.treeBatch.draw()
		self.drawCenterOfMass()
		self.drawCreatures()


	def rotateBillboard(self, pos):
		# Rotate the billboard frame up 90 and towards the player
		glRotatef(90,0,1,0)
		faceAngle = degrees(atan2(self.playerPosition.y - pos.y, self.playerPosition.x - pos.x))
		glRotatef(-faceAngle,1,0,0)


#================== SHARED DRAWING ==================#

	def drawUI(self):
		# Initialize Projection matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self.width, 0, self.height, -1, 1)

		# Initialize Modelview matrix
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		# Drawing
		glEnable(GL_BLEND)
		glDisable(GL_DEPTH_TEST)
		# Draw FPS display
		self.FPS.draw()
		# Draw UI controls
		if self.mode == "2D":
			self.bottomPanel.draw()
		glDisable(GL_BLEND)
		glEnable(GL_DEPTH_TEST)

	def drawCreatures(self):
		for herd in self.environment.herds:
			for creature in herd.creatures:
				self.drawSquare(creature.pos, creature.size, (1,1,1,1))
		for creature in self.selectedCreatures:
			self.drawSquare(creature.pos, creature.size*1.5, color=(1,0,0,1))

	def drawCenterOfMass(self):
		for herd in self.environment.herds:
			self.drawSquare(herd.getCenter(), 20, color=(0,1,0,1))

	def drawSelector(self):
		# Mouse selection box
		if self.leftClickTool == "select":
			glDisable(GL_DEPTH_TEST)
			glEnable(GL_BLEND)
			glColor4f(1,1,1,0.3)
			vertices = Models.rect(self.selectionStartX, self.selectionStartY, self.selectionEndX, self.selectionEndY)
			pyglet.graphics.vertex_list(len(vertices)//3, ("v3f/static", vertices)).draw(GL_QUADS)
			glEnable(GL_DEPTH_TEST)
			glEnable(GL_BLEND)

	def drawSquare(self, pos, size, color):
		glPushMatrix()
		glTranslatef(pos.x, pos.y, -pos.y)

		if self.mode == "3D":
			self.rotateBillboard(pos)

		# Get square data and draw
		glColor4f(*color)
		pyglet.graphics.vertex_list(4, ("v3f/static", Models.centeredSquare(size))).draw(GL_QUADS)
		
		glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		glColor4f(0,0,0,1)
		pyglet.graphics.vertex_list(4, ("v3f/static", Models.centeredSquare(size))).draw(GL_QUADS)
		
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		glPopMatrix()


class BillboardGroup(pyglet.graphics.Group):

	def __init__(self, objectPos, window, parent=None):
		self.objectPos = objectPos
		self.window = window
		super().__init__(parent)


	def set_state(self):
		if self.window.mode == "3D":
			glPushMatrix()
			glTranslatef(self.objectPos.x, self.objectPos.y, 0)
			glRotatef(90, 1,0,0)
			faceAngle = 90 - degrees(atan2(self.window.playerPosition.y - self.objectPos.y, self.window.playerPosition.x - self.objectPos.x))
			glRotatef(faceAngle, 0,-1,0)
			glTranslatef(-self.objectPos.x, -self.objectPos.y, 0)


	def unset_state(self):
		if self.window.mode == "3D":
			glPopMatrix()


if __name__ == '__main__':
	from Main import main
	main()