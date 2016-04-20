import random
from Vector import *
from Creature import *
from Herd import *

# ================ TODO ================
# * More complex behavior as described in the notes


class Environment(object):
# Should handle all interactions between creatures, herds, and environmental objects
# Assuming almost no user interaction?

	def __init__(self, gridSize, cellSize):
		# Width and height of the environment grid
		self.gridSize = gridSize
		self.cellSize = cellSize
		self.herds = []
		# Random environment elements
		self.land = []
		self.water = []
		self.trees = []
		self.shrubs = []
		self.rocks = []
		self.landProbability = 0.55
		self.treeProbability = 0.5
		self.shrubProbability = 0.5
		self.rockProbability = .05
		# 
		self.mutationRate = 0.5
		self.generateRandomEnvironment()

	def generateRandomEnvironment(self):
		# Clumps of trees, shrubs, water
		# uses cellular automata to generate

		# Terrain
		terrainGenerator = GOL(self.gridSize, self.gridSize, [4,5,6,7,8], [5,6,7,8])
		terrainGenerator.random(self.landProbability)
		terrainGenerator.borders()
		while not terrainGenerator.stable:
			terrainGenerator.generation()
		terrain = terrainGenerator.board
		for row in range(self.gridSize):
			for col in range(self.gridSize):
				if (row, col) in terrain:
					self.land.append((row, col))

		# Get water tiles immediately surrounding terrain
		terrainGenerator.stay = []
		terrainGenerator.begin = [2,3,4,5]
		terrainGenerator.generation()

		water = terrainGenerator.board
		for row in range(self.gridSize):
			for col in range(self.gridSize):
				if (row, col) in water:
					self.water.append((row, col))

		# Trees exist only on terrain
		treeGenerator = GOL(self.gridSize, self.gridSize, [4,5,6,7,8], [5,6,7,8])
		treeGenerator.random(self.treeProbability)
		treeGenerator.borders()
		while not treeGenerator.stable:
			treeGenerator.generation()
		trees = treeGenerator.board
		for row in range(self.gridSize):
			for col in range(self.gridSize):
				if (row, col) in terrain and (row, col) in trees:
					self.trees.append(Tree(col*self.cellSize + self.cellSize/2 + random.uniform(-self.cellSize/2, self.cellSize/2),
										   row*self.cellSize + self.cellSize/2 + random.uniform(-self.cellSize/2, self.cellSize/2)))

		# Shrubs are a lot like trees

		# Rocks are totally random



	#=============== USER ACTIONS ===============#

	def createHerd(self, N):
		herd = Herd()
		for n in range(N):
			herd.add(Creature(age=0, energy=100, size=10, pos=Vector(1000*random.random(), 1000*random.random(), 0)))
				# Position will be decided by the user
		self.herds.append(herd)


	def createSpecies(self):
		# randomly generate genetics/physiology
		pass


	def mate(creature1, creature2):
		newGenes = {}
		for gene in creature1.genes:
			newGenes[gene] = random.choice([creature1.genes[gene], creature2.genes[gene]])
			# Mutate
			newGenes[gene] += newGenes[gene] * self.mutationRate * random.uniform(-1,1)
		return Creature(age=0, energy=100, size=10, pos=Vector(0,0,0), vel=Vector(0,0,0), genes=newGenes)


	def update(self, dt):
		for herd in self.herds:
			herd.flock(dt)


class Tree:
# Randomizes a tree

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.rotAngle =    random.uniform(80,100)
		self.spreadAngle = random.uniform(15, 45)
		self.tiltAngle =   random.uniform(-40, 40)
		self.length =      random.uniform(5,15)
		self.thickness =   random.uniform(5,15)
		self.leafSize =    random.uniform(5,15)
		self.trunkColor =  [random.uniform(0.4,0.5), random.uniform(0.2,0.3), 0]
		self.leafColor =   [0, random.uniform(0.1,1), 0]

class Shrub:
# Randomizes a shrub

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.n =           random.randint(4,8)
		self.length =      random.uniform(5,15)
		self.spreadAngle = random.uniform(50, 120)
		self.curveAngle =  random.uniform(0, 40)
		self.tiltAngle =   random.uniform(-40, 40)
		self.thickness =   random.uniform(1, 10)
		self.color =       [0, random.uniform(0.1,1), 0]


class Rock:
	
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.n = random.randint(7, 12)
		self.r = random.uniform(5, 10)
		self.color = [random.uniform(0.1,0.3)]*3



class GOL:
# Cellular automata based on John Conway's Game of Life

	def __init__(self, rows, cols, stay=[2,3], begin=[3]):
		# Initialize board
		self.board = set()
		# Board dimensions
		self.rows = rows
		self.cols = cols
		# Game rules
		self.stay = stay
		self.begin = begin
		self.stable = False
		self.neighbors = [(-1,-1), (-1, 0), (-1, 1),
						  ( 0,-1),          ( 0, 1),
						  ( 1,-1), ( 1, 0), ( 1, 1)]

	def generation(self):
		# Temporary new empty board
		newBoard = set()
		# Loop through live cells in the board
		for cell in self.board:
			row, col = cell
			count = self.countNeighbors(row, col)
			# Cell continues to live based on "stay" rules
			for n in self.stay:
				if count == n:
					newBoard.add((row,col))
			# Evaluate dead neighbors
			for (dx, dy) in self.neighbors:
				# Wrap around horizontally and vertically
				newRow = (row + dy) % self.rows
				newCol = (col + dx) % self.cols
				# If the cell is dead
				if (newRow, newCol) not in self.board:
					count = self.countNeighbors(newRow, newCol)
					# Cell comes to life based on "begin" rules
					for n in self.begin:
						if count == n:
							newBoard.add((newRow, newCol))
		if self.board == newBoard:
			self.stable = True
		self.board = newBoard

	def countNeighbors(self, row, col):
		count = 0
		for (dx, dy) in self.neighbors:
			if ((row + dy) % self.rows, (col + dx) % self.cols) in self.board:
				count += 1
		return count

	def random(self, p):
		# p is the fraction of cells initialized as true
		self.board = set()
		for row in range(self.rows):
			for col in range(self.cols):
				if random.random() <= p:
					self.board.add((row,col))

	def borders(self):
		#TOP
		for col in range(self.cols):
			self.board.discard((0,col))
			self.board.discard((1,col))
		#BOTTOM
		for col in range(self.cols):
			self.board.discard((self.rows-1,col))
			self.board.discard((self.rows-2,col))
		#LEFT
		for row in range(self.rows):
			self.board.discard((row,0))
			self.board.discard((row,1))
		#RIGHT
		for row in range(self.rows):
			self.board.discard((row,self.cols-1))
			self.board.discard((row,self.cols-2))

	def upscale(self):
		pass

if __name__ == '__main__':
	from Main import main
	main()