import math

# ================ TODO ================
# Tree
# Bush
# Grass
# Water
# Rock
# Creature


class Models:
# Handles the visual translation of the environment into vertices/models for drawing
# For randomly generated things, all of the random attributes should be specified within Environment, 
# and the Models class should produce the same result every time a model is requested, based on those
# random attributes

	@staticmethod
	def tree(Tree):
		vertices = tuple()
		return vertices


	@staticmethod
	def grid(cellSize, gridSize):
		vertices = []
		for x in range(gridSize):
			for y in range(gridSize):
				vertices += [x*cellSize, y*cellSize, 0]
				vertices += [(x+1)*cellSize, y*cellSize, 0]
				vertices += [(x+1)*cellSize, (y+1)*cellSize, 0]
				vertices += [(x)*cellSize, (y+1)*cellSize, 0]
		return vertices


	@staticmethod
	def centeredSquare(size):
		vertices = ( size,  size, 0,
					-size,  size, 0,
					-size, -size, 0,
					 size, -size, 0 )
		return vertices


	@staticmethod
	def square(x, y, width, height):
		vertices = (x, y, 0,
					x+width, y, 0,
					x+width, y+height, 0,
					x, y+height, 0)
		return vertices