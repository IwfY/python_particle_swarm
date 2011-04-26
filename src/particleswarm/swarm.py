import math
from particleswarm.particle import Particle

class Swarm(object):
	"""
	representation of the particle swarm
	"""

	def __init__(self):
		self.__particles = []
		self.__dimensions = []
		self.__bestState = None
		self.__fitnessObject = None

	def findsolution(self, fitnessAccepted=0.0, maxTurns=100):
		pass

	def setFitnessObject(self, fitnessObject):
		self.__fitnessObject = fitnessObject


	def populate(self, particleCount=100, distribution="uniform", initialVelocityMethod="zero"):
		"""
		initialize particles that are spread over the problem space

		valid distribution mathods are:
			uniform
			random

		valid mathods to initialize the velocity of a particle
			zero		velocity is zero
			random		velocity is a random vector
		"""

		if self.dimensionCount() == 0:
			return False

		if particleCount < 1:
			return False

		if self.__fitnessObject == None:
			return False


		initialStates = [{}]

		if distribution == "uniform":
			particlesPerDimension = int(math.floor(math.pow(particleCount, 1 / self.dimensionCount())))
			if particlesPerDimension < 1:
				return False

			for dimension in self.__dimensions:
				stepPerState = (dimension[2] - dimension[1]) / (particlesPerDimension - 1)
				tmpStates = []
				rmStates = []
				for state in initialStates:
					for i in range(particlesPerDimension):
						tmpState = state.copy()
						tmpState[dimension[0]] = dimension[1] + i * stepPerState
						tmpStates.append(tmpState)
						#end for i in range(particlesPerDimension)

					rmStates.append(state)
					#end for state in initialStates

				for state in rmStates:
					initialStates.remove(state)

				initialStates.extend(tmpStates)
				#end for dimension in self.__dimensions
		elif distribution == "random":
			pass


		if initialVelocityMethod == "zero":
			velocity = {}
			for dimension in self.__dimensions:
				velocity[dimension[0]] = 0.0

			for state in initialStates:
				self.__particles.append(Particle(state, velocity.copy(), self.__fitnessObject))
		elif initialVelocityMethod == "random":
			pass

		return True

	def addDimension(self, name, lowerLimit=0.0, upperLimit=1.0):
		"""
		add a dimension to the problem space
		"""
		for (n, l, u) in self.__dimensions:
			if n == name:
				return False

		if lowerLimit > upperLimit:
			return False

		self.__dimensions.append((name, float(lowerLimit), float(upperLimit)))
		return True

	def dimensionCount(self):
		return len(self.__dimensions)

	def getDimensions(self):
		return self.__dimensions


	def getParticles(self):
		return self.__particles

	def getCurrentBestParticle(self):
		bestParticle = self.__particles[0]
		lowestFitness = bestParticle.fitness()

		for particle in self.__particles:
			currentFitness = particle.fitness()
			if currentFitness < lowestFitness:
				bestParticle = particle
				lowestFitness = currentFitness

		return bestParticle


	def getCurrentBestParticleFitness(self):
		bestParticle = self.getBestParticle()

		return bestParticle.fitness()

	def updateBestState(self):
		if self.getCurrentBestParticle().fitness() < self.__fitnessObject.fitness(self.__bestState):
			self.__bestState = self.getCurrentBestParticle().getState()


	def getBestFitness(self):
		"""
		get the fitness of the historical best known state
		"""
		return self.__fitnessObject.fitness(self.__bestState)
