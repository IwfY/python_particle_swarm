class Fitness(object):

	def __init__(self, name = '', buffering=False):
		self.__buffer = {}
		self.__buffering = buffering
		self.__name = name

	@staticmethod
	def stateToTuple(state):
		'''
		get a tuple containing concatenated keys and values of a state

		keys are sorted, after each key follows its value
		'''
		out = ()

		keyListSorted = [key for key in state.keys()]
		keyListSorted.sort()

		for key in keyListSorted:
			out += (key, state[key])

		return out

	def getName(self):
		return self.__name

	def setBuffering(self, buffering):
		'''
		turn buffering on or of
		'''
		self.__buffering = buffering


	def __getBufferedFitness(self, state):
		'''
		get a precalculated fitness for a given state

		@return precalculated fitness if existing in the buffer, None otherwise
		'''
		return self.__buffer.get(Fitness.stateToTuple(state), None)


	def __addFitnessToBuffer(self, state, fitness):
		'''
		add a calculated fitness to the buffer
		'''
		self.__buffer[Fitness.stateToTuple(state)] = fitness


	def fitness(self, state):
		'''
		get the fitness to a given state using the buffer
		'''
		if self.__buffering == True:
			buffered = self.__getBufferedFitness(state)
			if self.__getBufferedFitness(state) != None:
				return buffered

		fitness = self.calculateFitness(state)

		if self.__buffering == True:
			self.__addFitnessToBuffer(state, fitness)

		return fitness


	def calculateFitness(self, state):
		'''
		calculate the fitness to a given state
		'''
		raise NotImplemented("Please Implement this method.")
