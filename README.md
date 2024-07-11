Maryann Godje
Myles Andersson

Explanation of modifications to mcts_modified.py 
(aka, what changed between vanilla and modified):
    - changed the rollout() function in mcts_vanilla.py to be heuristic_rollout() in mcts_modified.py
        - while vanilla just chooses a random action, modified is more smart about what it chooses. 
            - If there is a chance to win, modified will place an X there. 
                - An example is if there's 2 X's in a row already, it will place the 3rd X. 
        - If the boxes are empty/not completed, it will resort to random selection like vanilla.
        - It will resort to random selection if there's no oppurtunity to win.
        - Overall, the heuristic rollout method we decided to use (constraint learning) is a simple one but it gets the job done!
    - called heuristic_rollout() in the simulation portion of MCTS in our think() function.