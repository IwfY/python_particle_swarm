from particleswarm.particle import Particle
import math
import multiprocessing
import os
import random
import sqlite3


# code to make methods able to be used by pickle
# see http://bytes.com/topic/python/answers/
#	         552476-why-cant-you-pickle-instancemethods
def _pickle_method(method):
	func_name = method.__func__.__name__
	obj = method.__self__
	cls = method.__self__.__class__
	return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
	for cls in cls.mro():
		try:
			func = cls.__dict__[func_name]
		except KeyError:
			pass
		else:
			break
	return func.__get__(obj, cls)

import copyreg
import types
copyreg.pickle(types.MethodType, _pickle_method, _unpickle_method)


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
		self.__processes = 1		# number of processes
		self.__pool = None


	def __del__(self):
		if self.__database:
			self.__database.close()


	def findSolution(self, fitnessAccepted=0.0, maxTurns=100):
		if len(self.__particles) == 0:
			return False

		if not self.__fitnessObject:
			return False

		self.writeParticlesToDatabase(0)

		for i in range(maxTurns):
			if self.__fitnessObject.fitness(self.__bestState) < fitnessAccepted:
				break
			self.step()
			self.writeParticlesToDatabase(i + 1)

		self.__updateBestState()

		return True


	def step(self):
		"""
		update velocity of all particles and move them
		"""
		for particle in self.__particles:
			particle.updateVelocity(self.__bestState,
									self.__vuMultiplier,
									self.__vuOldVelocityMultiplier,
									self.__vuGlobalBestStateMultiplier,
									self.__vuLocalBestStateMultiplier)
			particle.move()
		self.__updateBestState()


	def setFitnessObject(self, fitnessObject):
		"""
		set fitness object and propagate to particles
		"""
		self.__fitnessObject = fitnessObject
		for particle in self.__particles:
			particle.setFitnessObject(fitnessObject)


	def setVelocityUpdateParameters(self,
									multiplier,
									oldVelocityMultiplier,
									globalBestStateMultiplier,
									localBestStateMultiplier):
		self.__vuMultiplier = multiplier
		self.__vuOldVelocityMultiplier = oldVelocityMultiplier
		self.__vuGlobalBestStateMultiplier = globalBestStateMultiplier
		self.__vuLocalBestStateMultiplier = localBestStateMultiplier


	def setDatabase(self, dbName, continueWrite=False):
		"""
		create a database
		
		@param dbName string path to the database
		@param continueWrite boolean when true continue writing to the
			database if it already exists, when false throw a ValueError
			exception when attempting to overwrite an existing file
		"""

		if os.path.exists(dbName) and not continueWrite:
			raise ValueError()

		self.__database = sqlite3.connect(dbName)
		cur = self.__database.cursor()

		cur.execute("""CREATE TABLE IF NOT EXISTS particle_state
					(iteration INT, id INT, state VARCHAR(4096),
					velocity VARCHAR(4096), fitness FLOAT)""")
		self.__database.commit()
		cur.close()


	def loadParticlesFromDatabase(self, database, turn=-1):
		"""Delete all particles, populate swarm from particle states in
		a given turn from the database

		Attention: the output database is not set to the given database

		@param database the path to the database
		@param turn the turn from which the particle data should be
		choosen, if a negative value is given count backwards (e.g.
		turn = -2 means the second last turn)
		"""
		self.__particles = []

		try:
			inputDatabase = sqlite3.connect(database)
			cur = inputDatabase.cursor()
		except Exception:
			pass

		if turn < 0:
			cur.execute("SELECT MAX(iteration) FROM particle_state")
			queryParameters = (int(cur.fetchone()[0]) + turn + 1,)
		else:
			queryParameters = (turn,)

		cur.execute("""SELECT state, velocity
					   FROM particle_state
					   WHERE iteration = ?
					   ORDER BY id""",
					queryParameters)

		#result = cur.fetchall()

		for particle in cur:
			self.__particles.append(Particle(eval(particle[0]),
											 eval(particle[1]),
											 self.__fitnessObject))

		inputDatabase.close()

		self.__updateBestState()


	def writeParticlesToDatabase(self, turn):
		"""
		writes data about particles to database if available
		"""
		if self.__database == None:
			return

		cur = self.__database.cursor()
		for particle in self.__particles:
			cur.execute("""INSERT INTO particle_state (iteration, id, state, velocity, fitness) VALUES ({}, {}, "{}", "{}", {})""".format(turn, particle.getId(), str(particle.getState()), str(particle.getVelocity()), particle.fitness()))

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
			random.seed()

			for state in initialStates:
				velocity = {}
				for dimension in self.__dimensions:
					velocity[dimension[0]] = random.uniform(-(dimension[2] - dimension[1]) / 2, (dimension[2] - dimension[1]) / 2)
				self.__particles.append(Particle(state, velocity.copy(), self.__fitnessObject))

		self.__updateBestState()
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


	def getNumberOfProcesses(self):
		return self.__processes

	def setNumberOfProcesses(self, processes):
		assert(processes > 0)
		self.__processes = processes

		if processes > 1:
			self.__pool = multiprocessing.Pool(processes)
		else:
			self.__pool = None


	def getParticles(self):
		return self.__particles


	def getCurrentBestParticle(self):
		if not self.__particles:
			return None

		if self.__pool:
			stateList = []
			for particle in self.__particles:
				stateList.append(particle.getState())
			fitnessList = self.__pool.map(self.__fitnessObject.fitness, stateList)
			minFitness = min(fitnessList)
			listIndexOfMin = fitnessList.index(minFitness)

			return self.__particles[listIndexOfMin]
		else:
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
		if bestParticle == None:
			return None

		return bestParticle.fitness()

	def __updateBestState(self):
		if not self.__particles:
			return None

		if self.__bestState == None:
			self.__bestState = self.getCurrentBestParticle().getState()
		elif self.getCurrentBestParticleFitness() < self.__fitnessObject.fitness(self.__bestState):
			self.__bestState = self.getCurrentBestParticle().getState()


	def getBestFitness(self):
		"""
		get the fitness of the historical best known state
		"""
		if self.__fitnessObject == None or self.__bestState == None:
			return None

		return self.__fitnessObject.fitness(self.__bestState)

	def getBestState(self):
		return self.__bestState
