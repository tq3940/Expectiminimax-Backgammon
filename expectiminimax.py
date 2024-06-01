#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 23:39:49 2017

@author: chandu
"""
# from game_state import GameState
# from game import Backgammon
import copy
from draw_tree import Node
#import numpy as np

'''
player1: 1 -> 24
player2: 24-> 1

'''

infinity = float('inf')
player = 0
MAX_DEPTH = 4
dummy_action = [[0,0], [0,0]]
all_rolls = [[i,j] if i!=j else [i]*4 for i in range(1,7) for j in range(i,7)]

class GameState:
    def __init__(self, board, bar, player):
        self.board = board
        self.bar = bar
        self.player = player
        self.moves = []
            
    def can_bear_off(self,board, bar, player):
        '''
            This function checks if we can actually bear
            off a player
        '''
        bear_off = (bar[player] == 0)
        for i in range(1,19):
            index = (25 - i) if (2 == player) else i
            if bear_off:
                bear_off = (len(board[index]) == 0) or (board[index][0] != player)
        
        return bear_off
        
    def get_bear_off_move(self, board, roll, player):
        '''
            1. Check if direct bear offs are possible
            2. Check if inside home moves are possible
            3. Now check if jumps are possible
        '''
        
        poss_moves = []
        
        # this calculates direct moves
        index = (25 - roll) if (1 == player) else roll
        end = 0 if (2 == player) else 25
        if len(board[index]) != 0 and board[index][0] == player:
            poss_moves.append([index, end])
            
        # this calculates inside home moves
        for i in range(1, 6):
            index = 18 + i if (1 == player) else (7 - i)
            if 0 != len(board[index]) and board[index][0] == player:
                for j in range(1, 7 - i):
                    index2 = index - j if (2 == player) else index + j
                    if j == roll:
                        if (0 == len(board[index2])) or (1 == len(board[index2])) or (board[index2][0] == player):
                            poss_moves.append([index, index2])
                    
        
        if len(poss_moves)!=0:
            return poss_moves
        else:
            for i in range(1, 7):
                index = (25 - i) if (1 == player) else i
                end = 0 if (2 == player) else 25
                if len(board[index]) != 0 and board[index][0] == player:
                    if i<roll:
                        return [[index, end]]
        return poss_moves
                    
    def get_normal_moves(self, board, roll, player):
        '''
            this gets one possible move
        '''
        poss_moves = []
        for i in range(1, 24):
            index = (25 - i) if (2 == player) else i
            if 0 != len(board[index]) and board[index][0] == player:
                for j in range(1, min(7, 25 - i)):
                    index2 = (index - j) if (2 == player) else (index + j)
                    if j == roll:
                        if len(board[index2]) <= 1 or board[index2][0] == player:
                            poss_moves.append([index, index2])
                    
        return poss_moves
    
    
    def get_bar_move(self, board, roll, player):
        '''
            If the bar is not empty, then I am forced
            to remove the checkers from the bar first
        '''
        index = (25 - roll) if player == 2 else roll
        if len(board[index]) <= 1 or board[index][0] == player:
            return [-1, index]
        else:
            return []
    
    def get_moves(self, board, bar, dice_rolls, player, mv, moves):
        if len(dice_rolls)==0:
            moves.append(mv)
            return
        roll = dice_rolls[0]
        if bar[player] != 0:
            move = self.get_bar_move(board, roll, player)
            if len(move) != 0:
                bar[player] -= 1
                if len(board[move[1]]) == 1 and board[move[1]][0] != player:
                    board[move[1]].pop()
                board[move[1]].append(player)
                self.get_moves(board, bar, dice_rolls[1:], player, mv+[move], moves)
            else:
                self.get_moves(board, bar, dice_rolls[1:], player, mv, moves)
        else:
            if self.can_bear_off(board, bar, player):
                move = self.get_bear_off_move(board, roll, player)
            else:
                move = self.get_normal_moves(board, roll, player)
            if len(move) !=0:
                for m in move:
                    temp_board = copy.deepcopy(board)
                    temp_board[m[0]].pop()
                    if len(temp_board[m[1]]) == 1 and temp_board[m[1]][0] != player:
                        temp_board[m[1]].pop()
                    temp_board[m[1]].append(player)
                    self.get_moves(temp_board, bar, dice_rolls[1:], player, mv+[m], moves)
            else:
                self.get_moves(board, bar, dice_rolls[1:], player, mv, moves)


class Backgammon:
    def opponent(self, player):
        opp = {1:2, 2:1}
        return opp[player]
    
    def actions(self, state, dice_rolls):
        board = copy.deepcopy(state.board)
        bar = copy.deepcopy(state.bar)
        player = state.player
        moves = []
        if dice_rolls is not None:
            if len(dice_rolls) == 4:
                state.get_moves(copy.deepcopy(board), copy.deepcopy(bar), copy.deepcopy(dice_rolls), player, [], moves)
            else:
                m1 = []
                m2 = []
                state.get_moves(copy.deepcopy(board), copy.deepcopy(bar), copy.deepcopy(dice_rolls), player, [], m1)
                state.get_moves(copy.deepcopy(board), copy.deepcopy(bar), copy.deepcopy(list(reversed(dice_rolls))), player, [], m2)
                moves = m1 + m2
        return moves
    
    def result(self, state, move=None):
        board = copy.deepcopy(state.board)
        bar = copy.deepcopy(state.bar)
        # dice_roll = copy.deepcopy(state.dice_rolls)
        player = state.player
        if move is None:
            return GameState(board, bar, self.opponent(player))
        for m in move:
            if m[0] == -1:
                bar[player]-=1
                if len(board[m[1]]) == 1 and board[m[1]][0] != player:
                    bar[board[m[1]][0]]+= 1
                    board[m[1]].pop()
                board[m[1]].append(player)
            else:
                board[m[0]].pop()
                if len(board[m[1]]) == 1 and board[m[1]][0] != player:
                    bar[board[m[1]][0]]+= 1
                    board[m[1]].pop()
                
                board[m[1]].append(player)
        return GameState(board, bar, self.opponent(player))
    
    def utility(self, state, player):
        return None

def eval_fn(state):
    board = state.board
    m_player = player
    bar = state.bar
    v=0

    # 棋子离目的地的距离
    distance = 0
    for i in range(1, 25):
        if len(board[i]) > 0 and board[i][0] == m_player:
            distance+= len(board[i])*(abs(25 - i) if m_player==1 else abs(0-i))
    v = -1*distance

    # 在目标区域即将入槽的棋子数
    home_checkers = 0
    for i in range(1, 6):
        index = 18 + i if (1 == m_player) else (7 - i)
        if len(board[index])>0:
            home_checkers+=len(board[index])
    v+=home_checkers

    # 已入槽的棋子数
    v+=10*(len(board[25]) if m_player==1 else len(board[0]))

    # 当前被吃的棋子
    v-=10*bar[m_player]

    # 对方即将入槽的棋子数
    opponent_checkers = 0
    for i in range(1, 6):
        index = 18 + i if (2 == m_player) else (7 - i)
        if len(board[index])>0:
            opponent_checkers+=len(board[index])
    v-=opponent_checkers
    return v


'''
def minimaxnode(state, game, roll, depth):
    actions = game.actions(state, roll)
    v = 0

    if state.player == player:
        print('max player')
        score_fn = max
        v = -infinity
    else:
        score_fn = min
        depth-=1
    if not actions:
        return expectinode(game.result(state), game, depth)
    for a in actions:
        v = score_fn(v, expectinode(game.result(state,a), game, depth))
    return score_fn(roll_scores)
'''
def forward_pruning(state, actions, game, k=4):
    # 优化搜索顺序
    # 按各action的评估函数值从大到小排序action，优先搜索评估值大的action
    if len(actions) < k:
        return actions
    score_list = []
    new_action_list = []
    for a in actions:
        new_state = game.result(state,a)
        score_list.append(eval_fn(state))
    #arr = np.array(score_list)
    # 获取score_list中按元素从大到小排序后的索引的列表
    indices = sorted(range(len(score_list)), key=lambda i:score_list[i])[-k:][::-1]
    for i in indices:
        new_action_list.append(actions[i])
    return new_action_list

def max_value(state, game, roll, alpha, beta, depth):
    actions = game.actions(state, roll)
    actions = forward_pruning(state, actions, game)
    v = -infinity

    max_node = Node("max")

    if not actions:
        return expectinode(game.result(state), game, alpha, beta, depth)
    
    for action in actions:
        child_node,child_val = expectinode(game.result(state, action), game, alpha, beta, depth)

        v = max(v, child_val)
        max_node.add_child(child_node, "行动: "+str(action))

        if v >= beta:
            max_node.add_child(Node("cut", "cut"), "cut")
            max_node.set_val(v)
            return max_node,v
        
        alpha = max(alpha, v)

    max_node.set_val(v)
    return max_node,v
       
def min_value(state, game, roll, alpha, beta, depth):
    actions = game.actions(state, roll)
    actions = forward_pruning(state, actions, game)
    v = infinity
    depth-=1

    min_node = Node("min")

    if not actions:
        return expectinode(game.result(state), game, alpha, beta, depth)
    
    for action in actions:
        child_node,child_val = expectinode(game.result(state, action), game, alpha, beta, depth)

        v = min(v, child_val)
        min_node.add_child(child_node, "行动: "+str(action))

        if v <= alpha:
            min_node.add_child(Node("cut", "cut"), "cut")
            min_node.set_val(v)
            return min_node,v
        
        beta = min(beta, v)

    min_node.set_val(v)
    return min_node,v

def expectinode(state, game, alpha, beta, depth):

    if depth==0:
        eval_val = eval_fn(state)
        eval_node = Node("eval", eval_val)
        return eval_node,eval_val
    
    if player == state.player:
        fun = max_value
    else:
        fun = min_value

    chance_node = Node("chance")
    v = 0
    for roll in all_rolls:
        child_node,child_val = fun(state, game, roll, alpha, beta, depth)

        v+= (1/36 if len(roll) == 4 else 1/18) * child_val
        chance_node.add_child(child_node, "骰子点数: "+str(roll))
    
    chance_node.set_val(v)
    return chance_node,v

def get_best_move(state, game, dice_rolls):
    best_score = -infinity
    best_action = None
    beta = infinity

    depth = 1
    actions = game.actions(state, dice_rolls)
    actions = forward_pruning(state, actions, game)

    root = Node("max")

    for action in actions:
        chance_node,v = expectinode(game.result(state,action), game, best_score, beta, depth)
        
        root.add_child(chance_node, "行动: "+str(action))

        if v> best_score:
            best_score = v
            best_action = action

    root.set_val(best_score)

    return root,best_action
    
if __name__ == '__main__':
    board = []
    bar = []
    dice_rolls = []
    player = int(input())
    for i in range(26):
        x = list(map(int, input().strip().split()))
        if 2 == len(x):
            board.append([x[1]] * x[0])
        else:
            board.append([])

    bar.append(0)
    bar.append(int(input()))
    bar.append(int(input()))

    rolls = input()
    for i in range(int(rolls)):
        dice_rolls.append(int(input()))

    dice_rolls.sort()
    game_state = GameState(board, bar, player)
    game = Backgammon()

    #print(game.actions(game_state, dice_rolls))
    moves = get_best_move(game_state, game, dice_rolls)
    
    if moves is not None:
        print("\n".join(" ".join(str(m) for m in move) for move in moves))