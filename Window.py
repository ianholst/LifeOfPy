import pyglet
from pyglet.gl import *
from pyglet.window import key, mouse
from Vector import *
from Creature import *
from Herd import *
from Environment import *

class Window(pyglet.window.Window):
# main job is to draw the environment and allow the user to interact with it

	def __init__(self, environment):
		config = Config(sample_buffers=1, samples=2)
		super().__init__(caption="Herding Demo", resizable=False, vsync=False, config=config, fullscreen=True)

		self.environment = environment

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

		self.FPS = pyglet.clock.ClockDisplay(format="%(fps).1f", color=(0.5, 0.5, 0.5, 0.5))
		self.timeFactor = 1
		pyglet.clock.schedule(self.update)
		pyglet.app.run()

	def on_mouse_press(self, x, y, button, modifiers):
		worldClick = self.mouseToWorld(Vector(x,y))
		for herd in self.environment.herds:
			for creature in herd.creatures:
				if (creature.pos.x - creature.size <= worldClick.x <= creature.pos.x + creature.size and
					creature.pos.y - creature.size <= worldClick.y <= creature.pos.y + creature.size):
					self.environment.selectedCreature = creature
					break

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		# Dragging a selected creature
		if self.environment.selectedCreature != None:
			worldClick = self.mouseToWorld(Vector(x,y))
			self.environment.selectedCreature.pos = worldClick
			self.environment.selectedCreature.vel = Vector(0,0)
		# Panning the view
		else:
			self.viewLeft   -= dx * self.zoomLevel
			self.viewRight  -= dx * self.zoomLevel
			self.viewBottom -= dy * self.zoomLevel
			self.viewTop    -= dy * self.zoomLevel

	def on_mouse_release(self, x, y, button, modifiers):
		self.environment.selectedCreature = None

	def on_mouse_scroll(self, x, y, dx, dy):
		# Get scale factor
		f = self.zoomFactor**(-dy)
		# If zoomLevel is in the proper range
		if self.maxZoomIn < self.zoomLevel * f < self.maxZoomOut:
			self.zoomLevel *= f

			worldMousePos = self.mouseToWorld(Vector(x,y))
			worldX, worldY = worldMousePos.x, worldMousePos.y

			self.viewWidth *= f
			self.viewHeight *= f

			self.viewLeft   = worldX - x * (self.viewWidth / self.width)
			self.viewRight  = worldX - x * (self.viewWidth / self.width) + self.viewWidth
			self.viewBottom = worldY - y * (self.viewHeight / self.height)
			self.viewTop    = worldY - y * (self.viewHeight / self.height) + self.viewHeight

	def mouseToWorld(self, mousePos):
		worldX = self.viewLeft   + mousePos.x * (self.viewWidth  / self.width)
		worldY = self.viewBottom + mousePos.y * (self.viewHeight / self.height)
		return Vector(worldX, worldY)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.UP:
			self.timeFactor += 1
		elif symbol == key.DOWN:
			self.timeFactor -= 1
		elif symbol == key.ESCAPE:
			self.close()

	def on_resize(self, width, height):
		# TODO: fix this to take into account zoom level
		#self.viewRight = (self.viewWidth  / self.width) * width
		#self.viewTop = height
		#glViewport(int(self.viewLeft), int(self.viewBottom), int(self.viewRight), int(self.viewTop))
		pass

	def on_draw(self):
		self.clear()

		# Initialize Projection matrix
		glMatrixMode( GL_PROJECTION )
		glLoadIdentity()

		# Initialize Modelview matrix
		glMatrixMode( GL_MODELVIEW )
		glLoadIdentity()

		# Set orthographic projection matrix
		glOrtho(self.viewLeft, self.viewRight, self.viewBottom, self.viewTop, 1, -1 )
		self.drawCenterOfMass()
		self.drawCreatures()
		if self.environment.selectedCreature != None:
			self.drawSelector(self.environment.selectedCreature)
		
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self.width, 0, self.height, -1, 1)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		self.FPS.draw()

	def drawCreatures(self):
		for herd in self.environment.herds:
			for creature in herd.creatures:
				self.drawCircle(creature.pos.x, creature.pos.y, creature.size-2, creature.size)
				#drawPoint(creature.pos.x, creature.pos.y)
				pass

	def drawCircle(self, x, y, inner, outer, color=(1,1,1,0.5)):
		'''draws a ring of inner radius "inner" and outer radius "outer"
		   centered at (x, y).'''
		glPushMatrix()
		glColor4f(*color)
		glTranslatef(x, y, 0)
		q = gluNewQuadric()
		# a circle is written as a number of triangular slices; we use
		# a maximum of 360 which looked smooth even for a circle as
		# large as 1500 px.
		# Smaller circles can be drawn with fewer slices - the rule we
		# use amount to approximately 1 slice per px on the circumference
		slices = min(360, 6*outer)
		gluDisk(q, inner, outer, slices, 1)
		glPopMatrix()

	def drawSelector(self, creature):
		self.drawCircle(creature.pos.x, creature.pos.y, creature.size-3, creature.size, color=(1,0,0,1))

	def drawCenterOfMass(self):
		for herd in self.environment.herds:
			self.drawCircle(herd.getCenter().x, herd.getCenter().y, 0, 30, color=(0,0.5,0,1))

	def update(self, dt):
		self.environment.update(self.timeFactor*dt)



##################### MAIN #####################


#create herd
	#inside herd make creatures

environment = Environment()
environment.createHerd(100)
environment.createHerd(50)
window = Window(environment)