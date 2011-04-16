class Particle(object):
    '''
    class represents a single particle
    '''

    def __init__(self, state, velocity, fitnessObject):
        self.__state = state
        self.__bestState = state
        self.__velocity = velocity
        self.__fitnessObject = fitnessObject


    def fitness(self):
        '''
        returns the fitness of the particle
        '''
        return self.__fitnessObject.fitness(self.state)

    def move(self):
        '''
        move according to velocity and update own best state
        '''
        pass


    def updateVelocity(self, globalBestState, multiplier, oldVelocityMultiplier, globalBestStateMultiplier, localBestStateMultiplier):
        '''
        recalculate the velocity

        @param globalBestState Dictionary holding the global best state
        @param multiplier multiplier for the new velocity
        @param multiplier multiplier for the influence of the old velocity
        @param globalBestStateMultiplier multiplier for the influence of the global best to the velocity
        @param localBestStateMultiplier multiplier for the influence of the local best to the velocity
        '''

        for key in __state.keys():
            deltaVelocityGlobalBest[key] =  globalBestStateMultiplier * (globalBestState[key] - self.__state[key])
            deltaVelocityLocalBest[key] = localBestStateMultiplier * (self.__bestState[key] - self.__state[key])

            velocity[key] = multiplier * (oldVelocityMultiplier * velocity[key] + deltaVelocityGlobalBest[key] + deltaVelocityLocalBest[key])


    def getState(self):
        return self.__state


    def getBestState(self):
        return self.__bestState

    def getVelocity(self):
        return self.__velocity