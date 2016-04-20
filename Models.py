from math import *
import random

# ================ TODO ================
# Tree
# Shrub
# Rock
# Terrain
# Creature


class Models:
# Handles the visual translation of the environment into vertices/models for drawing
# For randomly generated things, all of the random attributes should be specified within Environment, 
# and the Models class should produce the same result every time a model is requested, based on those
# random attributes

	@staticmethod
	def terrain(gridSize, cellSize, land):
		vertices = []
		for y in range(gridSize):
			for x in range(gridSize):
				vertices += [x*cellSize, y*cellSize, -y*cellSize]
				vertices += [(x+1)*cellSize, y*cellSize, -y*cellSize]
				vertices += [(x+1)*cellSize, (y+1)*cellSize, -(y+1)*cellSize]
				vertices += [(x)*cellSize, (y+1)*cellSize, -(y+1)*cellSize]

		colors = []
		for y in range(gridSize):
			for x in range(gridSize):
				colors += [0,0,random.uniform(0.5,0.7)]*4
		for cell in land:
			row, col = cell
			startIndex = (row*gridSize + col)*12
			endIndex = (row*gridSize + col+1)*12
			colors[startIndex:endIndex] = [0,random.uniform(0.5,0.9),0]*4
		return vertices, colors


	@staticmethod
	def tree(Tree):
		# Unpack attributes
		spreadAngle = Tree.spreadAngle
		tiltAngle = Tree.tiltAngle

		def pythagorasTreeVertices(x1, y1, n, angle, length, thickness):
			vertices = []
			if n > 0:
				x2 = x1 + cos(radians(angle)) * length * n
				y2 = y1 + sin(radians(angle)) * length * n
				vertices += [x1-thickness/2 * cos(radians(90-angle)), y1+thickness/2 * sin(radians(90-angle)), 0,
							 x1+thickness/2 * cos(radians(90-angle)), y1-thickness/2 * sin(radians(90-angle)), 0,
							 x2+thickness/3 * cos(radians(90-angle)), y2-thickness/3 * sin(radians(90-angle)), 0,
							 x2-thickness/3 * cos(radians(90-angle)), y2+thickness/3 * sin(radians(90-angle)), 0]
				vertices += pythagorasTreeVertices(x2, y2, n-1, angle+spreadAngle-tiltAngle/2, length-1, thickness*2/3)
				vertices += pythagorasTreeVertices(x2, y2, n-1, angle-spreadAngle-tiltAngle/2, length-1, thickness*2/3)
				return vertices
			else:
				# Leaves
				vertices += Models.blob(x1, y1, 5, length*2)
				return vertices

		def pythagorasTreeColors(n):
			colors = []
			if n > 0:
				colors += Tree.trunkColor*4
				colors += pythagorasTreeColors(n-1)*2
				return colors
			else:
				colors += Tree.leafColor*4*5
				return colors

		vertices = pythagorasTreeVertices(Tree.x, Tree.y, 5, Tree.rotAngle, Tree.length, Tree.thickness)
		colors = pythagorasTreeColors(5)
		return vertices, colors


	@staticmethod
	def blob(x, y, n, r):
		angle = 2*pi/n
		startAngle = random.uniform(-angle,angle)
		vertices = []
		x2 = random.uniform(r/2, 3*r/2) * cos(startAngle)
		y2 = random.uniform(r/2, 3*r/2) * sin(startAngle)
		for s in range(n):
			x1 = x2
			y1 = y2
			x2 = random.uniform(r/2, 3*r/2) * cos((s+1)*angle+startAngle)
			y2 = random.uniform(r/2, 3*r/2) * sin((s+1)*angle+startAngle)
			vertices += [x,y,-.1, x,y,-.1, x+x1,y+y1,-.1, x+x2,y+y2,-.1]
		return vertices

	@staticmethod
	def shrub():
		pass


#	@staticmethod
#	def creature(Creature):
#		
#		def creatureVertices(elements, x, y):
#			vertices = []
#			for element in elements:
#				if type(element) != list:
#					if element["part"] == "core":
#						vertices += Models.circle(x, y, element["radius"], 50)
#					elif element["part"] == "limb":
#						pass
#				else:
#					angle = 2*pi/len(element)
#					for s in range(len(element)):
#						vertices += recurse(element[s], x+, y):
#			return vertices
#
#		vertices = recurse(Creature.body, Creature.pos.x, Creature.pos.y)


	def getCourse(courseCatalog, courseNumber):
		# Base case, course number is found at current level
		if courseNumber in courseCatalog:
			return courseCatalog[0] + "." + courseNumber
		else:
			for element in courseCatalog[1:]:
				if getCourse(element, courseNumber) != None:
					return courseCatalog[0] + "." + getCourse(element,courseNumber)
			# Dead end, go up
			return None





	@staticmethod
	def centeredSquare(size):
		vertices = [ size,  size, 0,
					-size,  size, 0,
					-size, -size, 0,
					 size, -size, 0]
		return vertices


	@staticmethod
	def square(x, y, width, height):
		vertices = [x, y, 0,
					x+width, y, 0,
					x+width, y+height, 0,
					x, y+height, 0]
		return vertices

	@staticmethod
	def rect(x1, y1, x2, y2):
		vertices = [x1, y1, 0,
					x1, y2, 0,
					x2, y2, 0,
					x2, y1, 0]
		return vertices

	@staticmethod
	def circle(x, y, r, n):
		vertices = []
		angle = 2*pi/n
		x2 = r
		y2 = 0
		for s in range(n):
			x1 = x2
			y1 = y2
			x2 = r * cos((s+1)*angle)
			y2 = r * sin((s+1)*angle)
			vertices += [x,y,0, x,y,0, x+x1,y+y1,0, x+x2,y+y2,0]
		return vertices

if __name__ == '__main__':
	from Main import main
	main()