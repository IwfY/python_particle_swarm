import os
import sqlite3


class SwarmSqliteExporter(object):
    def __init__(self, database_filename='swarm_run.sqlite', continueWrite=False):
        self.__database = None
        self.initDatabase(database_filename, continueWrite)

    def __del__(self):
        if self.__database:
            self.__database.close()

    def initDatabase(self, dbName, continueWrite=False):
        """
        create a database

        @param dbName string path to the database
        @param continueWrite boolean when true continue writing to the
                database if it already exists, when false throw a ValueError
                exception when attempting to overwrite an existing file
        """

        if os.path.exists(dbName) and not continueWrite:
            raise ValueError()

        self.__database = sqlite3.connect(dbName)
        cur = self.__database.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS particle_state
					(iteration INT, id INT, state VARCHAR(4096),
					velocity VARCHAR(4096), fitness FLOAT)""")
        self.__database.commit()
        cur.close()

    def writeParticles(self, swarm, turn):
        """
        writes data about particles to database if available
        """
        if self.__database == None:
            return

        cur = self.__database.cursor()
        for particle in swarm.getParticles():
            cur.execute("""INSERT INTO particle_state (iteration, id, state, velocity, fitness) VALUES ({}, {}, "{}", "{}", {})""".format(
                turn, particle.getId(), str(particle.getState()), str(particle.getVelocity()), particle.fitness()))

        self.__database.commit()
        cur.close()
