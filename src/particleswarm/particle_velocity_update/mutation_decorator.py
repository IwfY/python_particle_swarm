import random

class MutationDecorator:
	'''
	Decorator for particle velocity update strategy that multiplies one random velocity vector if velocity length is beneath a
	given threshold
	'''
	def __init__(self, particleVelocityUpdateStrategy, velocityMutationThreshold, mutationFactor = 100, mutationNumber = 1):
		self.__particleVelocityUpdateStrategy = particleVelocityUpdateStrategy
		self.__velocityMutationThresholdPow2 = pow(velocityMutationThreshold, 2)
		self.__mutationFactor = mutationFactor
		self.__mutationNumber = mutationNumber

	def setVelocityMutationThreshold(self, velocityMutationThreshold):
		self.__velocityMutationThresholdPow2 = pow(velocityMutationThreshold, 2)

	def setMutationFactor(self, mutationFactor):
		self.__mutationFactor = mutationFactor

	def setMutationNumber(self, mutationNumber):
		self.__mutationNumber = mutationNumber

	def getNewVelocity(self, particle):
		newVelocity = self.__particleVelocityUpdateStrategy.getNewVelocity(particle)

		lengthPow2 = sum(map(lambda x: x*x, newVelocity.values()))

		if lengthPow2 < self.__velocityMutationThresholdPow2:
			for c in range(0, self.__mutationNumber):
				keyToMutate = random.choice([i for i in newVelocity.keys()])
				#print("Mutate: {}, {}, {}, {}".format(particle.getId(), keyToMutate, newVelocity[keyToMutate], newVelocity[keyToMutate] * self.__mutationFactor))
				newVelocity[keyToMutate] *= self.__mutationFactor

		return newVelocity
