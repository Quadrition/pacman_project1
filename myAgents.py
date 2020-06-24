# myAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

from game import Agent
from searchProblems import PositionSearchProblem

from game import Directions

import util
import time
import search

"""
IMPORTANT
`agent` defines which agent you will use. By default, it is set to ClosestDotAgent,
but when you're ready to test your own agent, replace it with MyAgent
"""
def createAgents(num_pacmen, agent='MyAgent'):
    return [eval(agent)(index=i) for i in range(num_pacmen)]

class MyAgent(Agent):
    """
    Implementation of your agent.
    """

    def getAction(self, state):
        """
        Returns the next action the agent will take
        """

        global start
        global end
        # Counts the food at the begin
        global food_count

        # Initialize a number of food
        if not start:
            food_count = state.getNumFood()
            start = True

        # Checks if there are actions to apply
        if len(self.actions) == 0:
            # Checks if there are more food to search
            if end is False:
                # Initializes a new list of actions and takes the first one
                problem = AnyFoodSearchProblem(state, self.index)
                self.actions = search.bfs(problem)
                self.actions.reverse()
                return self.actions.pop()
            else:
                # Do nothing
                return Directions.STOP
        # Applies an action
        else:
            return self.actions.pop()

    def initialize(self):
        """
        Intialize anything you want to here. This function is called
        when the agent is first created. If you don't need to use it, then
        leave it blank
        """

        # Indicates if action is made first time
        global start
        start = False
        # Indicates if pacman targeted all food
        global end
        end = False

        # Represents a list of food that is being targeted
        global target_food
        target_food = []

        # Represents a list of actions that needs to be applied
        self.actions = []

class CoopAgent(Agent):
    """
    Implementation of your agent.
    """

    # Number of pacmans in the game
    pacman_count = 0
    # A list of foods that are currently being chased by pacman
    chasing_food = []

    def getAction(self, state):
        """
        Returns the next action the agent will take
        """

        # Checks if pacman has no food left to eat
        if not self.finished:
            # Checks if pacman applied all actions from the list
            if len(self.actions) == 0:
                self.actions = search.bfs(CoopFoodSearchProblem(state, self.index))
                self.actions.reverse()
            # Takes a next action from the list
            if len(self.actions) > 0:
                return self.actions.pop()
            # Pacman has no food left to eat
            else:
                self.finished = True
                return Directions.STOP
        return Directions.STOP

    def initialize(self):
        """
        Intialize anything you want to here. This function is called
        when the agent is first created. If you don't need to use it, then
        leave it blank
        """

        # Indicates if pacman has no food left
        self.finished = False
        # A list of actions for the pacman
        self.actions = []
        # Increase number of pacmans
        CoopAgent.pacman_count += 1

"""
Put any other SearchProblems or search methods below. You may also import classes/methods in
search.py and searchProblems.py. (ClosestDotAgent as an example below)
"""

class ClosestDotAgent(Agent):

    def findPathToClosestDot(self, gameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition(self.index)
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState, self.index)


        return search.bfs(problem)

    def getAction(self, state):
        return self.findPathToClosestDot(state)[0]

class AnyFoodSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any food.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below.  The state space and
    successor function do not need to be changed.

    The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test that will
        complete the problem definition.
        """
        x, y = state

        global target_food
        global end
        global food_count

        # Checks if state is food and it is not being targeted
        if state not in target_food and self.food[x][y]:
            # Targets the food
            target_food.append(state)
            # Indicates if pacman targeted all food
            if len(target_food) == food_count:
                end = True
            return True
        else:
            return False

class CoopFoodSearchProblem(PositionSearchProblem):
    '''
    Copyright notice: This class is original by Shaohua Yuan, Jing Xue has commented and improved
    '''

    def __init__(self, gameState, agentIndex):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition(agentIndex)
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0  # DO NOT CHANGE

        self.agent_index = agentIndex
        self.food_list = gameState.getFood().asList()
        average_food = len(self.food_list) // CoopAgent.pacman_count
        self.agent_food = self.food_list[agentIndex * average_food : (agentIndex + 1) * average_food]

    def isGoalState(self, state):
        # Check if there is food
        if state in self.food_list:
            # Return true if there are less food than pacmans
            if len(self.food_list) <= CoopAgent.pacman_count:
                return True
            # Returns true if food is pacman's and it is not chased
            if state in self.agent_food and state not in CoopAgent.chasing_food:
                CoopAgent.chasing_food.append(state)
                return True
            # Returns true if state is close to pacman position and is not chased
            elif (util.manhattanDistance(state, self.startState) <= (1 + self.agent_index) ** 2) \
                    and (state not in CoopAgent.chasing_food):
                CoopAgent.chasing_food.append(state)
                return True
            # Other situations
            else:
                return state in self.agent_food
        else:
            return False

