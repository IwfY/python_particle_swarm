class ParticleVelocityUpdateStrategy(object):

	def __init__(self, swarm):
		self.__swarm = swarm

	def getSwarm(self):
		return self.__swarm

	def getNewVelocity(self, particle):
		'''
		update the velocity of given particle
		'''
		raise NotImplemented("Please Implement this method.")
