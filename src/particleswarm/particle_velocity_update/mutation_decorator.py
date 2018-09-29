import random

class MutationDecorator:
	'''
	Decorator for particle velocity update strategy that multiplies one random velocity vector if velocity length is beneath a
	given threshold
	'''
	def __init__(self, particleVelocityUpdateStrategy, velocityMutationThreshold, mutationFactor = 100):
		self.__particleVelocityUpdateStrategy = particleVelocityUpdateStrategy
		self.__velocityMutationThresholdPow2 = pow(velocityMutationThreshold, 2)
		self.__mutationFactor = mutationFactor

	def setVelocityMutationThreshold(self, velocityMutationThreshold):
		self.__velocityMutationThresholdPow2 = pow(velocityMutationThreshold, 2)

	def getNewVelocity(self, particle):
		newVelocity = self.__particleVelocityUpdateStrategy.getNewVelocity(particle)

		lengthPow2 = sum(map(lambda x: x*x, newVelocity.values()))

		if lengthPow2 < self.__velocityMutationThresholdPow2:
			keyToMutate = random.choice([i for i in newVelocity.keys()])
			#print("Mutate: {}, {}, {}, {}".format(particle.getId(), keyToMutate, newVelocity[keyToMutate], newVelocity[keyToMutate] * self.__mutationFactor))
			newVelocity[keyToMutate] *= self.__mutationFactor

		return newVelocity
