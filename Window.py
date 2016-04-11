import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Herd import *
from Environment import *
from GUI import *
import math

# ================ TODO================
# * Change mouse cursor depending on operation
# * Add GUI elements
# * 3D shading
# * Resizing the window in 2D mode
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

		# GUI
		pyglet.resource.path = ["resources"]
		pyglet.resource.reindex()
		self.loadIcons()

		self.bottomPanel = BottomPanel(width=self.width, height=100)
		
		self.playPauseButton = Button(self.bottomPanel, anchor="left", icon=self.pauseIcon, f=self.playPause)
		Button(self.bottomPanel, anchor="left", icon=self.slowerIcon, f=self.slower)
		Button(self.bottomPanel, anchor="left", icon=self.fasterIcon, f=self.faster)

		Button(self.bottomPanel, anchor="center", text="Herd", icon=self.noIcon, f=lambda:self.environment.createHerd(20))

		Button(self.bottomPanel, anchor="right", text="3D", icon=self.noIcon, f=self.switchMode)
		Button(self.bottomPanel, anchor="right", text="woo", icon=self.noIcon, f=self.change)

		self.bottomPanel.layoutPanel()

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
		self.move = Vector(0,0,0)
		self.mouseSensitivity = 0.2
		self.FOV = 70

		# OpenGL setup
		glClearColor(0, 0, 0, 0)
		glEnable(GL_BLEND) # enable alpha channel
		#glEnable(GL_LINE_SMOOTH)
		#glEnable(GL_POLYGON_SMOOTH)
		#glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
		#glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
		glShadeModel(GL_FLAT)
		#glEnable(GL_CULL_FACE)
		#glEnable(GL_LIGHTING)
		#glEnable(GL_LIGHT0)
		#glEnable(GL_LIGHT1)
		#self.initFog()

		# Grid Model
		self.gridSize = 100
		self.cellSize = 10
		self.vertexData = []
		for x in range(self.gridSize):
			for y in range(self.gridSize):
				self.vertexData += [x*self.cellSize, y*self.cellSize, 0]
				self.vertexData += [(x+1)*self.cellSize, y*self.cellSize, 0]
				self.vertexData += [(x+1)*self.cellSize, (y+1)*self.cellSize, 0]
				self.vertexData += [(x)*self.cellSize, (y+1)*self.cellSize, 0]
		self.gridModel = pyglet.graphics.vertex_list(4*self.gridSize**2, "v3f/static")
		self.gridModel.vertices = self.vertexData

		self.creatureBatch = pyglet.graphics.Batch()


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

	def loadIcons(self):
		self.playIcon = pyglet.resource.image("play.png")
		self.pauseIcon = pyglet.resource.image("pause.png")
		self.slowerIcon = pyglet.resource.image("slower.png")
		self.fasterIcon = pyglet.resource.image("faster.png")
		self.noIcon = pyglet.resource.image("none.png")
		for icon in [self.playIcon,self.pauseIcon,self.slowerIcon,self.fasterIcon,self.noIcon]:
			icon.anchor_x = icon.width/2
			icon.anchor_y = icon.height/2


	def update(self, dt):
		if not self.paused:
			self.environment.update(self.timeFactor*dt)
		if self.mode == "3D":
			self.playerVelocity.x = self.playerSpeed * math.cos(math.radians(self.playerLook[0]) + math.atan2(self.move.y, self.move.x)) * bool(self.move.x or self.move.y)
			self.playerVelocity.y = self.playerSpeed * math.sin(math.radians(self.playerLook[0]) + math.atan2(self.move.y, self.move.x)) * bool(self.move.x or self.move.y)
			self.playerVelocity.z = self.playerSpeed * self.move.z
			self.playerPosition += self.playerVelocity * dt


#================== MOUSE EVENTS ==================#

	def on_mouse_press(self, x, y, button, modifiers):
		if self.mode == "2D":
			if self.bottomPanel.mouse_press(x, y):
				return

			if button == mouse.LEFT:
				worldClick = self.mouseToWorld(Vector(x,y,0))
				for herd in self.environment.herds:
					for creature in herd.creatures:
						if (creature.pos.x - creature.size <= worldClick.x <= creature.pos.x + creature.size and
							creature.pos.y - creature.size <= worldClick.y <= creature.pos.y + creature.size):
							self.environment.selectedCreature = creature
							break


	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		if self.mode == "2D":
			if buttons & mouse.LEFT:
				# Dragging a selected creature
				if self.environment.selectedCreature != None:
					worldClick = self.mouseToWorld(Vector(x,y,0))
					self.environment.selectedCreature.pos = worldClick
					self.environment.selectedCreature.vel = Vector(0,0,0)
				else: # do GUI stuff
					if self.bottomPanel.mouse_drag(x,y):
						return

			#if buttons & mouse.MIDDLE:
			if self.environment.selectedCreature == None:
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
				self.environment.selectedCreature = None
				self.bottomPanel.mouse_release(x, y)


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

				worldMousePos = self.mouseToWorld(Vector(x,y,0))
				worldX, worldY = worldMousePos.x, worldMousePos.y

				self.viewWidth *= f
				self.viewHeight *= f

				self.viewLeft   = worldX - x * (self.viewWidth / self.width)
				self.viewRight  = worldX - x * (self.viewWidth / self.width) + self.viewWidth
				self.viewBottom = worldY - y * (self.viewHeight / self.height)
				self.viewTop    = worldY - y * (self.viewHeight / self.height) + self.viewHeight
		elif self.mode == "3D":
			self.FOV *= self.zoomFactor**(-dy)
			self.mouseSensitivity *= self.zoomFactor**(-dy)


	def mouseToWorld(self, mousePos):
		worldX = self.viewLeft   + mousePos.x * (self.viewWidth  / self.width)
		worldY = self.viewBottom + mousePos.y * (self.viewHeight / self.height)
		return Vector(worldX, worldY,0)


	def on_resize(self, width, height):
		# Update the 2D viewport
		# TODO: fix this to take into account zoom level
		glViewport(0, 0, width, height)
		self.viewRight += (width * self.zoomLevel - self.viewWidth)
		self.viewTop += (height * self.zoomLevel - self.viewHeight)
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
				self.move.y += 1
			elif symbol == key.A:
				self.move.x -= 1
			elif symbol == key.S:
				self.move.y -= 1
			elif symbol == key.D:
				self.move.x += 1
			elif symbol == key.SPACE:
				self.move.z += 1
			elif symbol == key.LSHIFT:
				self.move.z -= 1


	def on_key_release(self, symbol, modifiers):
		if self.mode == "3D":
			if symbol == key.W:
				self.move.y -= 1
			elif symbol == key.A:
				self.move.x += 1
			elif symbol == key.S:
				self.move.y += 1
			elif symbol == key.D:
				self.move.x -= 1
			elif symbol == key.SPACE:
				self.move.z -= 1
			elif symbol == key.LSHIFT:
				self.move.z += 1


#================== BUTTON FUNCTIONS ==================#

	def playPause(self):
		if self.paused:
			self.paused = False
			self.playPauseButton.sprite.image = self.pauseIcon
		else:
			self.paused = True
			self.playPauseButton.sprite.image = self.playIcon

	def slower(self):

		self.timeFactor -= 1

	def faster(self):
		self.timeFactor += 1

	def switchMode(self):
		if self.mode == "2D":
			self.mode = "3D"
			self.set_exclusive_mouse(True)
			self.move = Vector(0,0,0)
		elif self.mode == "3D":
			self.mode = "2D"
			self.set_exclusive_mouse(False)
			self.move = Vector(0,0,0)

	def change(self):
		for i in range(len(self.gridModel.vertices)):
			if i%3 == 0:
				self.gridModel.vertices[i] += 10

#================== DRAWING ==================#

	def on_draw(self):
		self.clear()
		if self.mode == "2D":
			self.draw2D()
		elif self.mode == "3D":
			self.draw3D()
		self.drawInterface()

#================== 2D DRAWING ==================#


	def draw2D(self):
		glEnable(GL_DEPTH_TEST)
		self.drawEnvironment2D()
		self.drawGrid()

	def drawEnvironment2D(self):
		# Initialize Projection matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()

		# Initialize Modelview matrix
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		# Set orthographic projection matrix
		glOrtho(self.viewLeft, self.viewRight, self.viewBottom, self.viewTop, -1, 1)
		self.drawCenterOfMass()
		self.drawCreatures()
		if self.environment.selectedCreature != None:
			self.drawSelector(self.environment.selectedCreature)

	def drawSquare2D(self, pos, size, color):
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		glPushMatrix()
		glColor4f(*color)
		glTranslatef(pos.x, pos.y, pos.z)
		pyglet.graphics.vertex_list(4, ("v3f/static", self.getSquareVertices(size))).draw(GL_QUADS)
		glPopMatrix()


#================== 3D DRAWING ==================#

	def draw3D(self):
		glEnable(GL_DEPTH_TEST)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(self.FOV, self.width/self.height, 0.1, 10000)

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
		
		self.drawGrid()
		self.drawEnvironment3D()


	def drawEnvironment3D(self):
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		self.drawCreatures()
		self.drawCenterOfMass()
		if self.environment.selectedCreature != None:
			self.drawSelector(self.environment.selectedCreature)


	def drawSquare3D(self, pos, size, color):
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		glPushMatrix()
		glColor4f(*color)
		glTranslatef(pos.x, pos.y, pos.z)
		glRotatef(90,0,1,0)
		faceAngle = math.degrees(math.atan2(self.playerPosition.y - pos.y, self.playerPosition.x - pos.x))
		glRotatef(-faceAngle,1,0,0)
		pyglet.graphics.vertex_list(4, ("v3f/static", self.getSquareVertices(size))).draw(GL_QUADS)
		glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		glColor4f(0,0,0,1)
		pyglet.graphics.vertex_list(4, ("v3f/static", self.getSquareVertices(size))).draw(GL_QUADS)
		glPopMatrix()


#================== SHARED DRAWING ==================#


	def drawGrid(self):
		glColor4f(0, 0, 1, 1)
		glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		self.gridModel.draw(GL_QUADS)


	def drawInterface(self):
		# Initialize Projection matrix
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self.width, 0, self.height, -1, 1)

		# Initialize Modelview matrix
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		glDisable(GL_DEPTH_TEST)

		# Draw FPS display
		self.FPS.draw()
		# Draw UI controls
		if self.mode == "2D":
			self.bottomPanel.draw()

		glEnable(GL_DEPTH_TEST)


	def getSquareVertices(self, size):
		vertices = ( size,  size, 0,
					-size,  size, 0,
					-size, -size, 0,
					 size, -size, 0 )
		return vertices


	def drawCreatures(self):
		for herd in self.environment.herds:
			for creature in herd.creatures:
				if self.mode == "2D":
					self.drawSquare2D(creature.pos, creature.size, (1,1,1,1))
				elif self.mode == "3D":
					self.drawSquare3D(creature.pos, creature.size, (1,1,1,1))

	def drawSelector(self, creature):
		if self.mode == "2D":
			self.drawSquare2D(creature.pos, creature.size*1.5, color=(1,0,0,1))
		elif self.mode == "3D":
			self.drawSquare3D(creature.pos, creature.size*1.5, color=(1,0,0,1))

	def drawCenterOfMass(self):
		for herd in self.environment.herds:
			if self.mode == "2D":
				self.drawSquare2D(herd.getCenter(), 30, color=(0,1,0,1))
			elif self.mode == "3D":
				self.drawSquare3D(herd.getCenter(), 30, color=(0,1,0,1))


##################### MAIN #####################


#create herd
	#inside herd make creatures
def main():
	environment = Environment()
	window = Window(environment)

if __name__ == '__main__':
	main()