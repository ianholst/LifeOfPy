from math import *
import random

#================== TODO ==================#
# Creature


class Models:
# Handles the visual translation of the environment into vertices/models for drawing
# For randomly generated things, all of the random attributes should be specified within Environment, 
# and the Models class should produce the same result every time a model is requested, based on those
# random attributes
	circleSides = 20



	@staticmethod
	def terrain(gridSize, cellSize, land):
		vertices = []
		for y in range(gridSize):
			for x in range(gridSize):
				vertices += [x*cellSize, y*cellSize, 0]
				vertices += [(x+1)*cellSize, y*cellSize, 0]
				vertices += [(x+1)*cellSize, (y+1)*cellSize, 0]
				vertices += [(x)*cellSize, (y+1)*cellSize, 0]

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
				vertices += pythagorasTreeVertices(x2, y2, n-1, angle+spreadAngle-tiltAngle/2, length*1/2**(1/2), thickness*2/3)
				vertices += pythagorasTreeVertices(x2, y2, n-1, angle-spreadAngle-tiltAngle/2, length*1/2**(1/2), thickness*2/3)
				return vertices
			else:
				# Leaves
				vertices += Models.blob(x1, y1, Tree.leafN, Tree.leafSize)
				return vertices

		def pythagorasTreeColors(n):
			colors = []
			if n > 0:
				colors += Tree.trunkColor*4
				colors += pythagorasTreeColors(n-1)*2
				return colors
			else:
				colors += Tree.leafColor*4*Tree.leafN
				return colors

		vertices = pythagorasTreeVertices(Tree.x, Tree.y, Tree.n, Tree.rotAngle, Tree.length, Tree.thickness)
		colors = pythagorasTreeColors(Tree.n)
		return vertices, colors


	@staticmethod
	def blob(x, y, n, r):
		# The only randomly generated model
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
			vertices += [x,y,-.01, x,y,-.01, x+x1,y+y1,-.01, x+x2,y+y2,-.01]
		return vertices


	@staticmethod
	def shrub(Shrub):
		vertices = []
		for l in range(Shrub.leaves):
			x2 = Shrub.x
			y2 = Shrub.y
			for n in range(Shrub.n):
				x1 = x2
				y1 = y2
				angle = 90 - Shrub.spreadAngle/2 + Shrub.spreadAngle/(Shrub.leaves-1) * l + Shrub.tiltAngle/2
				angle -= (90-angle) / 90 * Shrub.curveAngle * n
				t1 = Shrub.thickness - Shrub.thickness / Shrub.n * n
				t2 = Shrub.thickness - Shrub.thickness / Shrub.n * (n+1)
				x2 = x1 + cos(radians(angle)) * Shrub.length
				y2 = y1 + sin(radians(angle)) * Shrub.length
				vertices += [x1-t1 * cos(radians(90-angle)), y1+t1 * sin(radians(90-angle)), 0,
							 x1+t1 * cos(radians(90-angle)), y1-t1 * sin(radians(90-angle)), 0,
							 x2+t2 * cos(radians(90-angle)), y2-t2 * sin(radians(90-angle)), 0,
							 x2-t2 * cos(radians(90-angle)), y2+t2 * sin(radians(90-angle)), 0]
		
		colors = Shrub.color*4*Shrub.n*Shrub.leaves
		return vertices, colors


	@staticmethod
	def creature(Creature):
		
		def partVertices(part, x, y, angle=0):
			vertices = []
			currentPart = part[0]
			# Get vertices of current part
			if currentPart["type"] == "core":
				vertices += Models.circle(x, y, currentPart["radius"])
			elif currentPart["type"] == "limb":
				x1, y1 = x, y
				x2, y2 = x + currentPart["length"]*cos(angle), y + currentPart["length"]*sin(angle)
				t = currentPart["thickness"]
				vertices += [x1 - t * cos(pi/2-angle), y1 + t * sin(pi/2-angle), 0,
							 x1 + t * cos(pi/2-angle), y1 - t * sin(pi/2-angle), 0,
							 x2 + t * cos(pi/2-angle), y2 - t * sin(pi/2-angle), 0,
							 x2 - t * cos(pi/2-angle), y2 + t * sin(pi/2-angle), 0]
			# If the part has children
			if len(part) > 1:
				children = part[1:]
				# Get anchor points and angles for children based on current part type and length
				if currentPart["type"] == "core":
					angles = [radians(children[n][0]["angle"]) + 2*pi/len(children)*n for n in range(len(children))]
					#anchors = [(x + currentPart["radius"]*cos(angle), y + currentPart["radius"]*sin(angle)) for angle in angles]
					anchors = [(x,y) for n in range(len(children))]
				if currentPart["type"] == "limb":
					angles = [pi + angle + 2*pi/(len(children)+1)*(n+1) for n in range(len(children))]
					anchors = [(x2,y2) for angle in angles]

				for (child, anchor, angle) in zip(children, anchors, angles):
					vertices += partVertices(child, anchor[0], anchor[1], angle)

			return vertices

		def partColors(part):
			colors = tuple()
			currentPart = part[0]
			if currentPart["type"] == "core":
				colors += currentPart["color"] * 4 * Models.circleSides
			elif currentPart["type"] == "limb":
				colors += currentPart["color"] * 4
			# If the part has children
			if len(part) > 1:
				children = part[1:]
				for child in children:
					colors += partColors(child)

			return colors

		# Find lowest y coordinate and shift everything up
		vertices = partVertices(Creature.body, 0, 0)
		bottom = min(vertices[1::3])
		for v in range(1,len(vertices),3):
			vertices[v] -= bottom

		# Find extreme x coordinates and shift everything so x=0 is at the center
		left = min(vertices[0::3])
		right = max(vertices[0::3])
		middle = (right-left)/2
		for v in range(0,len(vertices),3):
			vertices[v] -= middle

		colors = partColors(Creature.body)
		return vertices, colors


	@staticmethod
	def centeredSquare(size):
		vertices = [ size,  size, 0,
					-size,  size, 0,
					-size, -size, 0,
					 size, -size, 0]
		return vertices

	@staticmethod
	def rect(x1, y1, x2, y2):
		vertices = [x1, y1, 0,
					x1, y2, 0,
					x2, y2, 0,
					x2, y1, 0]
		return vertices

	@staticmethod
	def circle(x, y, r, n=circleSides):
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


def rotate(vector, matrix):
	pass



if __name__ == '__main__':
	from Main import main
	main()