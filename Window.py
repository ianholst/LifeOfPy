import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Herd import *
from Environment import *
from Models import *
from GUI import *
import math

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
		super(Window, self).__init__(caption="Herding Demo", vsync=False, 
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
		Button(self.bottomPanel, anchor="left", icon=GUI.slowerIcon, f=self.slower)
		Button(self.bottomPanel, anchor="left", icon=GUI.fasterIcon, f=self.faster)

		Button(self.bottomPanel, anchor="center", text="Herd", icon=GUI.noIcon, f=lambda:self.environment.createHerd(20))
		Button(self.bottomPanel, anchor="center", text="Herd", icon=GUI.noIcon, f=lambda:self.environment.createHerd(20))

		Button(self.bottomPanel, anchor="right", text="3D", icon=GUI.threeDIcon, f=self.switchMode)
		Button(self.bottomPanel, anchor="right", text="woo", icon=GUI.noIcon, f=self.change)

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
		self.playerSpeed = 100
		self.playerLook = (0, 90) # (xy rotation, z rotation)
		self.playerMove = Vector(0,0,0)
		self.mouseSensitivity = 0.2
		self.FOV = 70

		# OpenGL setup
		glClearColor(0, 0, 0, 0)
		glEnable(GL_BLEND) # enable alpha channel
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
		#glBlendFunc(GL_ONE_MINUS_DST_ALPHA,GL_DST_ALPHA)
		#glEnable(GL_LINE_SMOOTH)
		#glEnable(GL_POLYGON_SMOOTH)
		#glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
		#glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		self.initShading()
		#self.initFog()

		# Grid Model
		gridSize = 100
		self.gridModel = pyglet.graphics.vertex_list(4*gridSize**2, "v3f")
		self.gridModel.vertices = Models.grid(cellSize=10, gridSize=gridSize)

		#self.creatureBatch = pyglet.graphics.Batch()


		# Runtime things
		#self.set_exclusive_mouse(False)
		self.FPS = pyglet.clock.ClockDisplay(color=(0.5, 0.5, 0.5, 0.5))
		self.FPS.label.y = self.height-50
		self.timeFactor = 1
		pyglet.clock.schedule(self.update)
		pyglet.app.run()

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


	def update(self, dt):
		if not self.paused:
			self.environment.update(self.timeFactor*dt)
		if self.mode == "3D":
			self.playerVelocity.x = self.playerSpeed * math.cos(math.radians(self.playerLook[0]) + math.atan2(self.playerMove.y, self.playerMove.x)) * bool(self.playerMove.x or self.playerMove.y)
			self.playerVelocity.y = self.playerSpeed * math.sin(math.radians(self.playerLook[0]) + math.atan2(self.playerMove.y, self.playerMove.x)) * bool(self.playerMove.x or self.playerMove.y)
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
		if self.mode == "2D":
			self.mode = "3D"
			self.set_exclusive_mouse(True)
			self.playerMove = Vector(0,0,0)
		elif self.mode == "3D":
			self.mode = "2D"
			self.set_exclusive_mouse(False)
			self.playerMove = Vector(0,0,0)

	def change(self):
		for i in range(len(self.gridModel.vertices)):
			if i%3 == 0:
				self.gridModel.vertices[i] += 7

#================== DRAWING ==================#

	def on_draw(self):
		self.clear()
		if self.mode == "2D":
			self.drawEnvironment2D()
		elif self.mode == "3D":
			self.drawEnvironment3D()
			#pyglet.graphics.vertex_list(4, ("v3f", (0,0,0, 10,0,0, 10,10,10, 0,10,0))).draw(GL_TRIANGLES)
		self.drawInterface()

#================== 2D DRAWING ==================#

	def drawEnvironment2D(self):
		glEnable(GL_DEPTH_TEST)
		# Initialize Projection matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		# Initialize Modelview matrix
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		# Set orthographic projection matrix
		glOrtho(self.viewLeft, self.viewRight, self.viewBottom, self.viewTop, -1, 1)
		
		# Actual drawing
		self.drawGrid()
		self.drawCenterOfMass()
		self.drawCreatures()
		if self.selectedCreatures != None:
			self.drawSelector()


#================== 3D DRAWING ==================#

	def drawEnvironment3D(self):
		glEnable(GL_DEPTH_TEST)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(self.FOV, self.width/self.height, 1, 10000)

		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		# XY rotation
		glRotatef(-self.playerLook[0], 0, 0, 1)
		# Z rotation
		glRotatef(-self.playerLook[1], 
			math.cos(math.radians(self.playerLook[0])), 
			math.sin(math.radians(self.playerLook[0])), 
			0)
		# Translate from player position (move the world, not the camera)
		glTranslatef(-self.playerPosition.x, -self.playerPosition.y, -self.playerPosition.z)
		
		# Actual drawing
		self.drawGrid()
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		self.drawCreatures()
		self.drawCenterOfMass()
		if self.selectedCreatures != None:
			self.drawSelector()

	def makeBillboard(self, pos):
		# Create billboard
		glRotatef(90,0,1,0)
		faceAngle = math.degrees(math.atan2(self.playerPosition.y - pos.y, self.playerPosition.x - pos.x))
		glRotatef(-faceAngle,1,0,0)


#================== SHARED DRAWING ==================#


	def drawGrid(self):
		glColor4f(0, 0, 1, 1)
		glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		self.gridModel.draw(GL_QUADS)
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


	def drawInterface(self):
		# Initialize Projection matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self.width, 0, self.height, -1, 1)

		# Initialize Modelview matrix
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		glDisable(GL_DEPTH_TEST)

		# Draw FPS display
		self.FPS.draw()
		# Draw UI controls
		if self.mode == "2D":
			self.bottomPanel.draw()

		glEnable(GL_DEPTH_TEST)

	def drawCreatures(self):
		for herd in self.environment.herds:
			for creature in herd.creatures:
				self.drawSquare(creature.pos, creature.size, (1,1,1,1))

	def drawCenterOfMass(self):
		for herd in self.environment.herds:
			self.drawSquare(herd.getCenter(), 20, color=(0,1,0,1))

	def drawSelector(self):
		for creature in self.selectedCreatures:
			self.drawSquare(creature.pos, creature.size*1.5, color=(1,0,0,1))
		if self.leftClickTool == "select":
			vertices = (self.selectionStartX, self.selectionStartY, 0,
						self.selectionStartX, self.selectionEndY, 0,
						self.selectionEndX, self.selectionEndY, 0,
						self.selectionEndX, self.selectionStartY, 0)

			glPushMatrix()
			glDisable(GL_DEPTH_TEST)
			glEnable(GL_BLEND)
			glColor4f(1,1,1,0.3)

			#glTranslatef(pos.x, pos.y, pos.z)
			pyglet.graphics.vertex_list(4, ("v3f/static", vertices)).draw(GL_QUADS)
			glPopMatrix()
			glEnable(GL_DEPTH_TEST)


	def drawSquare(self, pos, size, color):
		glPushMatrix()
		glColor4f(*color)
		glTranslatef(pos.x, pos.y, pos.z)

		if self.mode == "3D":
			self.makeBillboard(pos)

		# Get square data and draw
		pyglet.graphics.vertex_list(4, ("v3f/static", Models.square(size))).draw(GL_QUADS)
		glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		glColor4f(0,0,0,1)
		pyglet.graphics.vertex_list(4, ("v3f/static", Models.square(size))).draw(GL_QUADS)
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		glPopMatrix()

##################### MAIN #####################


#create herd
	#inside herd make creatures
def main():
	environment = Environment()
	window = Window(environment)

if __name__ == '__main__':
	main()