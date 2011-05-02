from particleswarm.particle import Particle
import math
import os
import random
import sqlite3

class Swarm(object):
	"""
	representation of the particle swarm
	"""

	def __init__(self):
		self.__particles = []
		self.__dimensions = []
		self.__bestState = None
		self.__fitnessObject = None
		self.__vuMultiplier = 0.5
		self.__vuOldVelocityMultiplier = 0.3
		self.__vuGlobalBestStateMultiplier = 0.3
		self.__vuLocalBestStateMultiplier = 0.3
		self.__database = None

	def __del__(self):
		if self.__database != None:
			self.__database.close()


	def findsolution(self, fitnessAccepted=0.0, maxTurns=100):
		if len(self.__particles) == 0:
			return False
		
		self.writeParticlesToDatabase(0)

		for i in range(maxTurns):
			self.updateBestState()
			#print(i - 1,"current:" , self.getCurrentBestParticle().getId(), self.getCurrentBestParticle().fitness(), "global:", self.__bestState, self.__fitnessObject.fitness(self.__bestState))

			if self.__fitnessObject.fitness(self.__bestState) < fitnessAccepted:
				break
			for particle in self.__particles:
				#print("p" + str(particle.getId()), particle.getState(), particle.getVelocity(), particle.getBestState(), particle.fitness(), sep="\t")
				particle.updateVelocity(self.__bestState,
										self.__vuMultiplier,
										self.__vuOldVelocityMultiplier,
										self.__vuGlobalBestStateMultiplier,
										self.__vuLocalBestStateMultiplier)
				particle.move()
			self.writeParticlesToDatabase(i + 1)
				

		self.updateBestState()


	def setFitnessObject(self, fitnessObject):
		self.__fitnessObject = fitnessObject


	def setVelocityUpdateParameters(self,
									multiplier,
									oldVelocityMultiplier,
									globalBestStateMultiplier,
									localBestStateMultiplier):
		self.__vuMultiplier = multiplier
		self.__vuOldVelocityMultiplier = oldVelocityMultiplier
		self.__vuGlobalBestStateMultiplier = globalBestStateMultiplier
		self.__vuLocalBestStateMultiplier = localBestStateMultiplier

	def setDatabase(self, dbName):
		"""
		create a database
		"""

		if os.path.exists(dbName):
			return False

		self.__database = sqlite3.connect(dbName)
		cur = self.__database.cursor()

		cur.execute("CREATE TABLE particle_state (iteration INT, id INT, state VARCHAR(4096), velocity VARCHAR(4096), fitness FLOAT)")
		self.__database.commit()
		cur.close()

	def writeParticlesToDatabase(self, turn):
		"""
		writes data about particles to database if available
		"""
		if self.__database == None:
			return
		
		cur = self.__database.cursor()
		for particle in self.__particles:
			cur.execute("""INSERT INTO particle_state (iteration, id, state, velocity, fitness) VALUES ({}, {}, "{}", "{}", {})""".format(turn, particle.getId(), particle.getState(), particle.getVelocity(), particle.fitness()))

		self.__database.commit()
		cur.close()

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


		initialStates = []

		if distribution == "uniform":
			particlesPerDimension = int(math.floor(math.pow(particleCount, 1 / self.dimensionCount())))
			if particlesPerDimension < 1:
				return False

			initialStates.append({})
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
			random.seed()
			for i in range(particleCount):
				tmpState = {}
				for dimension in self.__dimensions:
					tmpState[dimension[0]] = random.uniform(dimension[1], dimension[2])
				initialStates.append(tmpState.copy())


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
		bestParticle = self.getCurrentBestParticle()

		return bestParticle.fitness()

	def updateBestState(self):
		if self.__bestState == None:
			self.__bestState = self.getCurrentBestParticle().getState()
		elif self.getCurrentBestParticleFitness() < self.__fitnessObject.fitness(self.__bestState):
			self.__bestState = self.getCurrentBestParticle().getState()


	def getBestFitness(self):
		"""
		get the fitness of the historical best known state
		"""
		return self.__fitnessObject.fitness(self.__bestState)

	def getBestState(self):
		return self.__bestState
