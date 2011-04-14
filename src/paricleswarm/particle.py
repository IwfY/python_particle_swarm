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


    def move(self, globalBestState):
        '''
        recalculate the velocity, move accordingly, update own best state
        '''
        pass


    def getState(self):
        return self.__state


    def getBestState(self):
        return self.__bestState

    def getVelocity(self):
        return self.__velocity