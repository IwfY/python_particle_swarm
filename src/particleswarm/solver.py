import math
from particleswarm.default_particle_velocity_update_strategy import DefaultParticleVelocityUpdateStrategy
from particleswarm.particle_velocity_update.mutation_decorator import MutationDecorator
from particleswarm.swarm import Swarm

class ParticleSwarmSolver(object):
	"""
	representation of a problem to be solved by a particle swarm
	"""

	def __init__(self, problemName, fitnessObject, dimensions, populationInformation = [128, "random", "random"], particleVelocityUpdateStrategy=None):
		self.__problemName = problemName
		self.__fitnessObject = fitnessObject
		self.__dimensions = dimensions
		self.__populationCount, self.__initDistributionMethod, self.__initVelocityMethod = populationInformation
		self.__elasticSearchServer = None
		self.__elasticSearchIndex = None
		self.__elasticSearchThreshold = None

		self.__swarm = Swarm()
		self.__swarm.setFitnessObject(self.__fitnessObject)

		if particleVelocityUpdateStrategy is not None:
			self.__swarm.setParticleVelcityUpdateStrategyObject(particleVelocityUpdateStrategy)
		else:
			particleVelocityUpdateStrategy = DefaultParticleVelocityUpdateStrategy(self.__swarm, 0.6, 0.3, 0.3, 0.3)
			decoratedParticleVelocityUpdateStrategy = MutationDecorator(\
				particleVelocityUpdateStrategy, velocityMutationThreshold=30, mutationFactor=4000, mutationNumber=len(self.__dimensions) // 4)
			self.__swarm.setParticleVelcityUpdateStrategyObject(decoratedParticleVelocityUpdateStrategy)

		for dimensionsName, dimnesionMin, dimensionMax in dimensions:
			self.__swarm.addDimension(dimensionsName, dimnesionMin, dimensionMax)

		self.__swarm.populate(self.__populationCount, self.__initDistributionMethod, self.__initVelocityMethod)

	def setElasticSearchServer(self, serverBaseUrl, indexName, fitnessThreshold=100000):
		self.__elasticSearchServer = serverBaseUrl
		self.__elasticSearchIndex = indexName
		self.__elasticSearchThreshold = fitnessThreshold

	def getSwarm(self):
		return self.__swarm

	def solve(self, iterations, targetFitness=None, postStepFunction=None):
		if self.__elasticSearchServer is not None:
			self.__swarm.writeParticlesToElasticSearch(self.__elasticSearchServer, self.__elasticSearchIndex, 0, self.__elasticSearchThreshold)

		lastGlobalBestFitness = 999000000000
		for i in range(1, iterations + 1):
			self.__swarm.step()

			if self.__elasticSearchServer is not None:
				self.__swarm.writeParticlesToElasticSearch(self.__elasticSearchServer, self.__elasticSearchIndex, i, self.__elasticSearchThreshold)

			currentBestParticle = self.__swarm.getCurrentBestParticle()
			currentBestState = currentBestParticle.getState()
			currentBestFitness = self.__swarm.getCurrentBestParticleFitness()
			print('~~~~~~~ ' + str(i) + '/' + str(iterations) + ' ~~~~~~~~~~~~~~~~~~~')
			print('Id: ' + str(currentBestParticle.getId()))
			print(currentBestState)
			print('Velo length: ' + str(round(math.sqrt(currentBestParticle.getSqrVelocityVectorLength()), 5)))
			print(round(currentBestFitness, 2))
			if (currentBestFitness < lastGlobalBestFitness):
				print('   New Best. Delta: ' + str(round(lastGlobalBestFitness - currentBestFitness, 2)))
				lastGlobalBestFitness = currentBestFitness

			if postStepFunction is not None:
				postStepFunction(self.__swarm)

			if targetFitness is not None and currentBestFitness <= targetFitness:
				break

		return [self.__swarm.getBestState(), self.__swarm.getBestFitness()]
