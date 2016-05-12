import random
import numpy as np


class Environment:
# Handles all interactions between creatures and environmental objects

	def __init__(self, gridSize, cellSize, terrainResolution):
		# Width and height of the environment grid
		self.gridSize = gridSize
		self.cellSize = cellSize
		self.terrainResolution = terrainResolution

		self.species = []
		self.herds = []
		self.creatures = []
		self.positions = np.zeros(shape=(0,2))
		self.velocities = np.zeros(shape=(0,2))

		# Random environment elements
		self.landProbability = 0.55
		self.treeProbability = 0.5
		self.shrubProbability = 0.5
		self.rockProbability = .05
		self.generateRandomEnvironment()

		# If mutation rate is 1, properties can change up to 100% each generation
		self.mutationRate = 0.5


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

		# Trees exist only on terrain
		treeGenerator = GOL(self.gridSize, self.gridSize, [4,5,6,7,8], [5,6,7,8])
		treeGenerator.random(self.treeProbability)
		treeGenerator.borders()
		while not treeGenerator.stable:
			treeGenerator.generation()
		trees = treeGenerator.board
		self.trees = []
		for row in range(self.gridSize):
			for col in range(self.gridSize):
				if (row, col) in terrain and (row, col) in trees:
					self.trees.append(Tree(col*self.cellSize + self.cellSize/2 + random.uniform(-self.cellSize/2, self.cellSize/2),
										   row*self.cellSize + self.cellSize/2 + random.uniform(-self.cellSize/2, self.cellSize/2)))

		# Shrubs are a lot like trees
		shrubGenerator = GOL(self.gridSize, self.gridSize, [4,5,6,7,8], [5,6,7,8])
		shrubGenerator.random(self.shrubProbability)
		shrubGenerator.borders()
		while not shrubGenerator.stable:
			shrubGenerator.generation()
		shrubs = shrubGenerator.board
		self.shrubs = []
		self.shrubPositions = []
		for row in range(self.gridSize):
			for col in range(self.gridSize):
				if (row, col) in terrain and (row, col) in shrubs:
					x = col*self.cellSize + self.cellSize/2 + random.uniform(-self.cellSize/2, self.cellSize/2)
					y = row*self.cellSize + self.cellSize/2 + random.uniform(-self.cellSize/2, self.cellSize/2)
					self.shrubs.append(Shrub(x, y))
					self.shrubPositions.append((x,y))
		self.shrubPositions = np.array(self.shrubPositions)

		# Rocks are totally random
		self.rocks = []
		for row in range(self.gridSize):
			for col in range(self.gridSize):
				if random.random() < self.rockProbability and (row, col) in terrain:
					self.rocks.append(Rock(col*self.cellSize + self.cellSize/2 + random.uniform(-self.cellSize/2, self.cellSize/2),
										   row*self.cellSize + self.cellSize/2 + random.uniform(-self.cellSize/2, self.cellSize/2)))


		# Increase the resolution of the terrain
		while terrainGenerator.rows < self.terrainResolution:
			terrainGenerator.upscale()
		terrain = terrainGenerator.board
		self.land = []
		for row in range(self.terrainResolution):
			for col in range(self.terrainResolution):
				if (row, col) in terrain:
					self.land.append((row, col))

		# Get water tiles immediately surrounding terrain
		terrainGenerator.stay = []
		terrainGenerator.begin = [2,3,4,5]
		terrainGenerator.generation()

		water = terrainGenerator.board
		self.water = []
		for row in range(self.terrainResolution):
			for col in range(self.terrainResolution):
				if (row, col) in water:
					x = (col + 1/2) * self.gridSize / self.terrainResolution * self.cellSize
					y = (row + 1/2) * self.gridSize / self.terrainResolution * self.cellSize
					self.water.append((x, y))
		self.waterPositions = np.array(self.water)


	def update(self, dt):
		# Main AI implementation

		# Separations
		posDifferences = self.positions[:,None] - self.positions
		distances = np.sqrt(np.sum(posDifferences**2, axis=2))
		
		waterPosDifferences = self.positions[:,None] - self.waterPositions
		waterDistances = np.sqrt(np.sum(waterPosDifferences**2, axis=2))
		
		separationInfluences = np.zeros(shape=(len(self.creatures),2))
		avoidWater = np.zeros(shape=(len(self.creatures),2))
		seekCenter = np.zeros(shape=(len(self.creatures),2))
		matchVelocity = np.zeros(shape=(len(self.creatures),2))
		otherBehaviors = np.zeros(shape=(len(self.creatures),2))

		for i in range(len(self.creatures)):
			# Universal collision avoidance and water repulsion
			tooClose = distances[i] < self.creatures[i].width/2
			tooCloseIndices = np.nonzero(tooClose)
			influences = posDifferences[i, tooCloseIndices]
			separationInfluences[i] = np.sum(influences, axis=1)

			waterTooClose = waterDistances[i] < self.creatures[i].width/4
			waterTooCloseIndices = np.nonzero(waterTooClose)
			waterInfluences = waterPosDifferences[i, waterTooCloseIndices]
			avoidWater[i] = np.sum(waterInfluences, axis=1) * self.creatures[i].genes["moveTowardsFactor"]

			# State logic
			
			# Die if out of energy
			if self.creatures[i].energy < 0:
				self.remove(self.creatures[i])
			# Break away and search for food if necessary
			if self.creatures[i].state == "herding":
				if self.creatures[i].energy < self.creatures[i].genes["strength"]:
					self.creatures[i].state = "eating"
					self.creatures[i].herd.leave(self.creatures[i])

			if self.creatures[i].state == "eating":
				if self.creatures[i].type == "herbivore":
					# Find a plant to target
					shrubDistances = np.sqrt(np.sum((self.shrubPositions - self.positions[i])**2, axis=1))
					closest = np.argmin(shrubDistances[np.nonzero(shrubDistances)], axis=0)
					if shrubDistances[closest] < self.creatures[i].width/2:
						# Done
						self.creatures[i].energy += 100
						self.creatures[i].state = "herding"
						self.creatures[i].herd.join(self.creatures[i])
					else:
						otherBehaviors[i] = (self.shrubPositions[closest] - self.positions[i])

				elif self.creatures[i].type == "carnivore":
					preyDistances = np.sqrt(np.sum((self.positions - self.positions[i])**2, axis=1))
					closest = np.argmin(preyDistances[np.nonzero(preyDistances>0.0001)], axis=0)
					if self.creatures[i].target == None:
						# Find a creature to target
						self.creatures[i].target = self.creatures[closest]
						self.creatures[i].target.herd.attacker = self.creatures[i]
						self.creatures[i].target.herd.state = "fleeing"
					else:
						if preyDistances[closest] < self.creatures[i].width/2:
							# Done
							self.creatures[i].energy += self.creatures[closest].energy
							self.creatures[i].state = "herding"
							self.creatures[i].herd.join(self.creatures[i])
							# Clean up the body parts
							self.remove(self.creatures[closest])
							separationInfluences = np.delete(separationInfluences, self.creatures[closest].id, axis=0)
							avoidWater = np.delete(avoidWater, self.creatures[closest].id, axis=0)
							seekCenter = np.delete(seekCenter, self.creatures[closest].id, axis=0)
							matchVelocity = np.delete(matchVelocity, self.creatures[closest].id, axis=0)
							otherBehaviors = np.delete(otherBehaviors, self.creatures[closest].id, axis=0)
							# Calm down the herd
							#self.creatures[i].target.herd.attacker = None
							self.creatures[i].target.herd.state = "herding"
							self.creatures[i].target = None
							break
						else:
							otherBehaviors[i] = (self.positions[closest] - self.positions[i])


		# Herding behaviors
		for herd in self.herds:
			if len(herd.creatures) != 0:
				herdIndices = np.array([creature.id for creature in herd.creatures])
				if herd.state == "herding":
					CM = np.mean(self.positions[herdIndices], axis=0)
					CMV = np.mean(self.velocities[herdIndices], axis=0)
					for i in np.nditer(herdIndices):
						seekCenter[i] = (CM - self.positions[i]) * self.creatures[i].genes["cohesionFactor"]
						matchVelocity[i] = (CMV - self.velocities[i]) * self.creatures[i].genes["velocityMatchingFactor"]

				elif herd.state == "fleeing":
					attackerPos = self.positions[herd.attacker.id]
					for i in np.nditer(herdIndices):
						otherBehaviors[i] = -(attackerPos - self.positions[i]) * self.creatures[i].genes["moveTowardsFactor"]
		
		self.velocities += (seekCenter + matchVelocity + separationInfluences + avoidWater + otherBehaviors)
		# Limit speeds and deplete energy
		speeds = np.sqrt(np.sum(self.velocities**2, axis=1))
		for i in range(len(self.creatures)):
			if speeds[i] > self.creatures[i].genes["speed"]:
				self.velocities[i] = self.velocities[i] / speeds[i] * self.creatures[i].genes["speed"]
			# Energy loss is inversely proportional to strength and directly proportional to distance traveled
			self.creatures[i].energy -= speeds[i] / self.creatures[i].genes["strength"] * dt * 10
		# Update position
		self.positions += self.velocities * dt


	#=============== USER ACTIONS ===============#

	def add(self, creature, herd, x, y):
		creature.id = len(self.creatures)
		self.creatures.append(creature)
		self.positions = np.append(self.positions, np.array([[x, y]]), axis=0)
		self.velocities = np.append(self.velocities, np.array([[0, 0]]), axis=0)
		herd.join(creature)

	def remove(self, creature):
		# Pretty much just murder
		creature.herd.leave(creature)
		self.creatures.pop(creature.id)
		self.positions = np.delete(self.positions, creature.id, axis=0)
		self.velocities = np.delete(self.velocities, creature.id, axis=0)
		# shift indices
		for i in range(creature.id, len(self.creatures)):
			self.creatures[i].id -= 1

	def mate(self, creature1, creature2):

		# cycle through body recursively
		def recurse(part1, part2):
			newBody = []
			newPart = {}
			chosen = random.choice([part1[0], part2[0]])
			newPart["type"] = chosen["type"]
			newPart["color"] = random.choice([part1[0]["color"], part2[0]["color"]])
			newPart["angle"] = 0
			# Part-specific options
			if part1[0]["type"] == part2[0]["type"]:
				if newPart["type"] == "core":
					newPart["radius"] = random.choice([part1[0]["radius"], part2[0]["radius"]])
					newPart["radius"] += newPart["radius"] * self.mutationRate * random.uniform(-1,1)
				elif newPart["type"] == "limb":
					newPart["length"] = random.choice([part1[0]["length"], part2[0]["length"]])
					newPart["length"] += newPart["length"] * self.mutationRate * random.uniform(-1,1)
					newPart["thickness"] = random.choice([part1[0]["thickness"], part2[0]["thickness"]])
					newPart["thickness"] += newPart["thickness"] * self.mutationRate * random.uniform(-1,1)
				elif newPart["type"] == "mouth":
					newPart["radius"] = random.choice([part1[0]["radius"], part2[0]["radius"]])
					newPart["radius"] += newPart["radius"] * self.mutationRate * random.uniform(-1,1)
			else:
				if newPart["type"] == "core":
					newPart["radius"] = chosen["radius"]
					newPart["radius"] += newPart["radius"] * self.mutationRate * random.uniform(-1,1)
				elif newPart["type"] == "limb":
					newPart["length"] = chosen["length"]
					newPart["length"] += newPart["length"] * self.mutationRate * random.uniform(-1,1)
					newPart["thickness"] = chosen["thickness"]
					newPart["thickness"] += newPart["thickness"] * self.mutationRate * random.uniform(-1,1)
				elif newPart["type"] == "mouth":
					newPart["radius"] = chosen["radius"]
					newPart["radius"] += newPart["radius"] * self.mutationRate * random.uniform(-1,1)

			newBody.append(newPart)

			# If the parts have children
			if len(part1) != 1 and len(part2) != 1:
				for child1, child2 in zip(part1[1:], part2[1:]):
					newBody.append(recurse(child1, child2))
			return newBody

		newBody = recurse(creature1.body, creature2.body)

		if creature1.species.name == creature2.species.name:
			newName = creature1.species.name
		else:
			newName = creature1.species.name + " x " + creature2.species.name
		newSpecies = Species(name=newName, body=newBody)
		self.species.append(newSpecies)
		mainParent = random.choice([creature1, creature2])
		x = self.positions[mainParent.id, 0]
		y = self.positions[mainParent.id, 1]
		self.add(Creature(species=newSpecies), herd=mainParent.herd, x=x, y=y)




class Herd:
# Manages groups of creatures

	def __init__(self, species):
		# Initialize main data structure
		self.species = species
		self.type = species.type
		if self.type == "herbivore":
			self.attacker = None
		self.state = "herding"
		self.creatures = []

	def join(self, creature):
		creature.herd = self
		self.creatures.append(creature)

	def leave(self, creature):
		i = self.creatures.index(creature)
		self.creatures.pop(i)


class Creature:

	def __init__(self, species):
		self.state = "herding"
		self.type = species.type
		if self.type == "carnivore":
			self.target = None
		self.species = species
		self.body = species.body
		self.genes = species.genes
		self.energy = 2*self.genes["strength"]




class Species:
# Defines genetic parameters for creating creatures

	def __init__(self, name, body=None, genes=None):
		self.name = name
		# randomly generate genetics/physiology
		if body == None and genes == None:
			self.body = self.generateBody()
			self.genes = self.generateGenes()
		
		# Genetics passed in from mating
		else:
			self.body = body
			self.genes = self.generateGenes()


	def generateBody(self):
		# Some generic starting parameters

		def recurse(level):
			body = []
			part = {}
			part["type"] = random.choice(["core", "core", "limb", "limb", "mouth"])
			part["color"] = [random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)]
			part["angle"] = 0
			# Part-specific options
			if part["type"] == "core":
				part["radius"] = random.uniform(0.5,3)
			elif part["type"] == "limb":
				part["length"] = random.uniform(6,12)
				part["thickness"] = random.uniform(0.1,2)
			elif part["type"] == "mouth":
				part["radius"] = random.uniform(0.5,3)
			body.append(part)
			# Stop once the specified level is reached
			if level > 1:
				children = random.randint(1,6)
				for child in range(children):
					body.append(recurse(level-1))
			return body
		
		levels = random.randint(1,4)
		body = recurse(levels)
		return body


	def generateGenes(self):
		strengthFactor = 100
		speedFactor = 1
		ferocityFactor = 1
		genes = {}

		def recursiveCount(part):
			cores, limbs, mouths = 0,0,0
			currentPart = part[0]
			if currentPart["type"] == "core":
				cores += 1
			elif currentPart["type"] == "limb":
				limbs += 1
			elif currentPart["type"] == "mouth":
				mouths += 1
			# If the part has children
			if len(part) > 1:
				children = part[1:]
				for child in children:
					c, l, m = recursiveCount(child)
					cores += c
					limbs += l
					mouths += m
			return cores, limbs, mouths

		cores, limbs, mouths = recursiveCount(self.body)
		# More cores means stronger
		genes["strength"] = (cores+1) * strengthFactor
		# More limbs means faster
		genes["speed"] = (limbs+1) * speedFactor
		# More mouths means more likely to be a predator
		genes["ferocity"] = (mouths+1) * ferocityFactor
		if genes["ferocity"] >= 3:
			self.type = "carnivore"
		else:
			self.type = "herbivore"

		# Random genes not dependent on physiology
		genes["cohesionFactor"] = 1/random.uniform(50, 100)
		genes["velocityMatchingFactor"] = 1/random.uniform(100, 1000)
		genes["moveTowardsFactor"] = 1

		return genes




class Tree:
# Randomizes a tree

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.n =           5
		self.rotAngle =    random.uniform(80,100)
		self.spreadAngle = random.uniform(15, 45)
		self.tiltAngle =   random.uniform(-40, 40)
		self.length =      random.uniform(1,3)
		self.thickness =   random.uniform(1,2)
		self.leafSize =    random.uniform(1,3)
		self.leafN =       5
		self.trunkColor =  [random.uniform(0.4,0.5), random.uniform(0.2,0.4), 0]
		self.leafColor =   [random.uniform(0,0.2), random.uniform(0.1,1), 0]


class Shrub:
# Randomizes a shrub

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.n =           4
		self.leaves =      random.randint(4,8)
		self.length =      random.uniform(.5,1)
		self.spreadAngle = random.uniform(50, 120)
		self.curveAngle =  random.uniform(0, 40)
		self.tiltAngle =   random.uniform(-10, 10)
		self.thickness =   random.uniform(.1, 1)
		self.color =       [random.uniform(0,0.2), random.uniform(0.5,1), 0]


class Rock:
# Randomizes a rock

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.n = random.randint(7, 15)
		self.r = random.uniform(1, 3)
		self.color = [random.uniform(0.2,0.3)]*3



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
		newBoard = set()
		for row in range(self.rows):
			for col in range(self.cols):
				if (row, col) in self.board:
					newBoard.add((2*row,   2*col))
					newBoard.add((2*row+1, 2*col))
					newBoard.add((2*row,   2*col+1))
					newBoard.add((2*row+1, 2*col+1))
		self.rows *= 2
		self.cols *= 2
		self.board = newBoard
		# Apply upscaling algorithm
		self.stay = [5,6,7,8]
		self.begin = [5,6,7,8]
		self.generation()



if __name__ == '__main__':
	from Main import main
	main()