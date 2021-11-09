from particleswarm.particle_velocity_update_strategy import ParticleVelocityUpdateStrategy


class DefaultParticleVelocityUpdateStrategy(ParticleVelocityUpdateStrategy):

    def __init__(self, swarm, multiplier=0.6, oldVelocityMultiplier=0.3, globalBestStateMultiplier=0.3, localBestStateMultiplier=0.3):
        '''
        @param multiplier multiplier for the new velocity
        @param oldVelocityMultiplier multiplier for the influence of the old velocity
        @param globalBestStateMultiplier multiplier for the influence of the global best to the velocity
        @param localBestStateMultiplier multiplier for the influence of the local best to the velocity
        '''
        ParticleVelocityUpdateStrategy.__init__(self, swarm)
        self.__multiplier = multiplier
        self.__oldVelocityMultiplier = oldVelocityMultiplier
        self.__globalBestStateMultiplier = globalBestStateMultiplier
        self.__localBestStateMultiplier = localBestStateMultiplier

    def getNewVelocity(self, particle):
        '''
        update the velocity of given particle
        '''
        globalBestState = self.getSwarm().getBestState()
        particleState = particle.getState()
        particleBestState = particle.getBestState()
        currentParticleVelocity = particle.getVelocity()

        newParticleVelocity = {}
        for key in particleState:
            deltaVelocityGlobalBest = self.__globalBestStateMultiplier * (globalBestState[key] - particleState[key])
            deltaVelocityLocalBest = self.__localBestStateMultiplier * (particleBestState[key] - particleState[key])

            newParticleVelocity[key] = self.__multiplier * (self.__oldVelocityMultiplier * currentParticleVelocity[key] + deltaVelocityGlobalBest + deltaVelocityLocalBest)

        return newParticleVelocity
