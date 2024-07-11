
from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

num_nodes = 500
explore_faction = 2.

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """ Traverses the tree until the end criterion are met.
    e.g. find the best expandable node (node with untried action) if it exist,
    or else a terminal node

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 1 or 2

    Returns:
        node: A node from which the next stage of the search can proceed.
        state: The state associated with that node

    """
    while not board.is_ended(state):
        if node.untried_actions:
            return node, state
        
        #find the child with the best UCB score
        best_score = float('-inf')
        best_child = None
        best_action = None
        for action, child in node.child_nodes.items():
            score = ucb(child, board.current_player(state) != bot_identity)
            if score > best_score:
                best_score = score
                best_child = child
                best_action = action

        if best_child is None:
            return node, state
        
        node = best_child
        state = board.next_state(state, best_action)

    return node, state
    #pass

def expand_leaf(node: MCTSNode, board: Board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node (if it is non-terminal).

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:
        node: The added child node
        state: The state associated with that node

    """

    if not node.untried_actions:
        return node, state
    
    action = node.untried_actions.pop()
    next_state = board.next_state(state, action)
    child_node = MCTSNode(parent = node, parent_action = action, action_list = board.legal_actions(next_state))
    node.child_nodes[action] = child_node

    return child_node, next_state
    #pass


def heuristic_rollout(board: Board, state, bot_identity: int):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.
    
    Returns:
        state: The terminal game state

    """
    while not board.is_ended(state):
        actions = board.legal_actions(state)
        if not actions:
            break

        # Quick check for box completion
        for action in actions:
            next_state = board.next_state(state, action)
            if board.owned_boxes(next_state) != board.owned_boxes(state):
                state = next_state
                break
        else:
            # If no box completion, choose a random action
            state = board.next_state(state, choice(actions))

    return state
    #pass

def backpropagate(node: MCTSNode|None, won: bool):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    while node is not None:
        node.visits += 1
        node.wins += int(won)
        node = node.parent
    #nothing to return.
    #pass

def ucb(node: MCTSNode, is_opponent: bool):
    """ Calcualtes the UCB value for the given node from the perspective of the bot

    A function to figure out which node to traverse to based on number of wins and visits.

    Args:
        node:   A node.
        is_opponent: A boolean indicating whether or not the last action was performed by the MCTS bot
    Returns:
        The value of the UCB function for the given node
    """
    # negative = loss
    # positive = win
    # 0 = draw (check at the end)

    # UCB = win rate + exploration factor * sqrt(ln(total visits) / visits from this node)
    # win rate = wins / visits
    # exploration factor = 2

    if node.visits == 0:
        return float('inf') # if the node has not been visited, visit it (may change later?)
    
    win_rate = node.wins / node.visits
    exploration = explore_faction * sqrt(log(node.parent.visits) / node.visits)
    if is_opponent:
        win_rate = 1 - win_rate
    return win_rate + exploration
    
    #pass

def get_best_action(root_node: MCTSNode):
    """ Selects the best action from the root node in the MCTS tree

    Args:
        root_node:   The root node
    Returns:
        action: The best action from the root node
    
    """

    best_action = None
    best_score = float('-inf')
    for action, child in root_node.child_nodes.items():
        if child.visits > best_score:
            best_score = child.visits
            best_action = action

    return best_action

    #pass

def is_win(board: Board, state, identity_of_bot: int):
    # checks if state is a win state for identity_of_bot
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        current_state:  The current state of the game.

    Returns:    The action to be taken from the current state

    """
    bot_identity = board.current_player(current_state) # 1 or 2
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))

    for _ in range(num_nodes):
        state = current_state
        node = root_node

        # Do MCTS - This is all you! 
        # beginning of our work

        # Selection
        node, state = traverse_nodes(node, board, state, bot_identity)

        # Expansion
        node, state = expand_leaf(node, board, state)

        # Simulation
        simulation_result = heuristic_rollout(board, state, bot_identity)


        # Backpropagation
        backpropagate(node, is_win(board, simulation_result, bot_identity))

    # end of our work

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_action = get_best_action(root_node)
    
    print(f"Action chosen: {best_action}")
    return best_action
