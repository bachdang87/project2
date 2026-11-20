# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
     # 1. Thắng / Thua
        if successorGameState.isWin():
            return float('inf')
        if successorGameState.isLose():
            return float('-inf')

        score = successorGameState.getScore()

        # 2. Phạt nhẹ khi đứng yên
        if action == Directions.STOP:
            score -= 10

        # 3. Thức ăn: gần hạt gần nhất + càng ít hạt còn lại càng tốt
        foodList = newFood.asList()
        if foodList:
            minFoodDist = min(manhattanDistance(newPos, f) for f in foodList)
            score += 10.0 / max(minFoodDist, 1)
        score -= 4 * len(foodList)

        # 4. Capsule: khuyến khích ăn nhẹ
        capsules = successorGameState.getCapsules()
        if capsules:
            minCapDist = min(manhattanDistance(newPos, c) for c in capsules)
            score += 3.0 / max(minCapDist, 1)
        score -= 10 * len(capsules)

        # 5. Ma
        for ghostState, scaredTime in zip(newGhostStates, newScaredTimes):
            dist = manhattanDistance(newPos, ghostState.getPosition())

            if scaredTime > 0:
                # Ma đang sợ: đuổi theo nếu kịp trước khi hết sợ
                if dist < scaredTime:
                    score += 100.0 / (dist + 1)
            else:
                # Ma thường: tuyệt đối không đi sát, và né dần khi lại gần
                if dist <= 1:
                    return float('-inf')
                if dist <= 4:
                    score -= 6.0 / dist

        return score
        return successorGameState.getScore()

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        numAgents = gameState.getNumAgents()
        def minimax(state, agentIndex, depth):
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)
            actions = state.getLegalActions(agentIndex)
            if not actions:
                return self.evaluationFunction(state)
            nextAgent = (agentIndex + 1) % numAgents
            nextDepth = depth + 1 if nextAgent == 0 else depth
            values = [minimax(state.generateSuccessor(agentIndex, a), nextAgent, nextDepth)
                      for a in actions]
            if agentIndex == 0:
                return max(values)
            return min(values)
        bestScore = float('-inf')
        bestAction = None
        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)
            value = minimax(successor, 1, 0)
            if value > bestScore:
                bestScore = value
                bestAction = action
        return bestAction


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and
        self.evaluationFunction
        """

        numAgents = gameState.getNumAgents()

        def alphaBeta(state, agentIndex, depth, alpha, beta):

            # Dieu kien dung
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)

            actions = state.getLegalActions(agentIndex)

            if not actions:
                return self.evaluationFunction(state)

            nextAgent = (agentIndex + 1) % numAgents
            nextDepth = depth + 1 if nextAgent == 0 else depth

            # MAX: Pacman
            if agentIndex == 0:
                value = float('-inf')

                for action in actions:
                    successor = state.generateSuccessor(agentIndex, action)

                    childValue = alphaBeta(
                        successor, nextAgent, nextDepth, alpha, beta
                    )

                    value = max(value, childValue)

                    # Alpha-Beta pruning
                    if value > beta:
                        return value

                    alpha = max(alpha, value)

                return value

            # MIN: Ghost
            else:
                value = float('inf')

                for action in actions:
                    successor = state.generateSuccessor(agentIndex, action)

                    childValue = alphaBeta(
                        successor, nextAgent, nextDepth, alpha, beta
                    )

                    value = min(value, childValue)

                    # Alpha-Beta pruning
                    if value < alpha:
                        return value

                    beta = min(beta, value)

                return value

        # Tim hanh dong tot nhat cua Pacman
        alpha = float('-inf')
        beta = float('inf')

        bestScore = float('-inf')
        bestAction = None

        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)

            value = alphaBeta(successor, 1, 0, alpha, beta)

            if value > bestScore:
                bestScore = value
                bestAction = action

            alpha = max(alpha, bestScore)

        return bestAction


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        numAgents = gameState.getNumAgents()

        def expectimax(state, agentIndex, depth):
            # Điều kiện dừng: thắng/thua hoặc đã tìm đủ độ sâu
            if state.isWin() or state.isLose() or depth == self.depth:
                return self.evaluationFunction(state)

            actions = state.getLegalActions(agentIndex)
            if not actions:
                return self.evaluationFunction(state)

            nextAgent = (agentIndex + 1) % numAgents
            # Chỉ tăng độ sâu sau khi tất cả agent (Pacman + mọi ma) đã đi xong
            nextDepth = depth + 1 if nextAgent == 0 else depth

            values = [expectimax(state.generateSuccessor(agentIndex, a), nextAgent, nextDepth)
                      for a in actions]

            if agentIndex == 0:
                # Pacman: MAX
                return max(values)
            # Ma: EXPECTATION (chọn đều ngẫu nhiên)
            return sum(values) / len(values)

        # Ở gốc: Pacman chọn hành động có giá trị kỳ vọng cao nhất,
        # nếu hòa thì chọn ngẫu nhiên để tránh đứng yên ở góc
        bestScore = float('-inf')
        bestActions = []
        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)
            value = expectimax(successor, 1, 0)
            if value > bestScore:
                bestScore = value
                bestActions = [action]
            elif value == bestScore:
                bestActions.append(action)
        return random.choice(bestActions)
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
