class Fitness(object):

	def __init__(self):
		self.__buffer = {}

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
		returns the fitness to a given state
		'''
		raise NotImplemented("Please Implement this method.")
