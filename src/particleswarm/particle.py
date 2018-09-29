class Particle(object):
	'''
	class represents a single particle
	'''

	__lastId = 1

	def __init__(self, state, velocity, fitnessObject, particleVelocityUpdateStrategy):
		self.__id = Particle.__lastId
		Particle.__lastId += 1
		self.__state = state
		self.__bestState = state.copy()
		self.__velocity = velocity
		self.__fitnessObject = fitnessObject
		self.__particleVelocityUpdateStrategy = particleVelocityUpdateStrategy


	def fitness(self):
		'''
		returns the fitness of the particle
		'''
		return self.__fitnessObject.fitness(self.__state)

	def setVelcityUpdateStrategyObject(self, particleVelocityUpdateStrategy):
		"""
		set fitness object and propagate to particles
		"""
		self.__particleVelocityUpdateStrategy = particleVelocityUpdateStrategy

	def move(self):
		'''
		move according to velocity and update own best state
		'''
		if self.__fitnessObject == None:
			return False

		for key in self.__state.keys():
			self.__state[key] = self.__state[key] + self.__velocity[key]

		#update local best fitness
		if (self.fitness() < self.__fitnessObject.fitness(self.__bestState)):
			self.__bestState = self.__state.copy()

		return True


	def updateVelocity(self):
		'''
		recalculate the velocity
		'''
		self.__velocity = self.__particleVelocityUpdateStrategy.getNewVelocity(self)


	def setVelocity(self, velocity):
		self.__velocity = velocity


	def getSqrVelocityVectorLength(self):
		out = 0
		for key in self.__velocity.keys():
			out += self.__velocity[key] * self.__velocity[key]

		return out

	def getId(self):
		return self.__id

	def getState(self):
		return self.__state

	def setState(self, state):
		self.__state = state

	def getBestState(self):
		return self.__bestState

	def setFitnessObject(self, fitnessObject):
		self.__fitnessObject = fitnessObject

	def getVelocity(self):
		return self.__velocity

	def resetVelocity(self):
		for key in self.__velocity.keys():
			self.__velocity[key] = 0.0

	def resetLocalBest(self):
		self.__localBest = self.__state.copy()
