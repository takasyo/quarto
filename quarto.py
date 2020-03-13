import random
import sys
import textwrap
import argparse
import pickle
import copy
from enum import Enum, IntEnum
from Player import Player, NPC, QNPC
from GameInfo import FieldInfo, QInfo
from View import View


class Difficulty(Enum):
    NORMAL = 0
    HARD = 1

class Turn(IntEnum):
    PLAYER = 0
    NPC = 1

class NPCType(IntEnum):
    NPC = 0
    QNPC = 1

class GameOverType(IntEnum):
    NOTOVER = 0
    DRAW = 1
    WIN = 2


class Qarto(object):
    def __init__(self, _game_mode=Difficulty.NORMAL):
        self.view = View()
        self.player = Player("Player")

        FieldInfo.resetFieldParams()

        if _game_mode == Difficulty.HARD:
            FieldInfo.changeDifficulty()
            self.view.dispTitleHard()
        else:
            self.view.dispTitleNormal()

    
    def gameIsOver(self, _current_player):
        for i in range(len(FieldInfo.clear_patterns)): # 0~9 or 0~18
            tmp = [1] * 4
            has_empty_slot = False
            for search_index in FieldInfo.clear_patterns[i]: #ex)[0, 4, 8, 12]
                if FieldInfo.selectedSlotIsEmpty(search_index):
                    has_empty_slot = True
                    break
    
                for str_index in [x for x, y in enumerate(tmp) if y == 1]: 
                    # tmpが1のindexだけ調べる
                    if FieldInfo.field_status[FieldInfo.clear_patterns[i][0]][str_index] != FieldInfo.field_status[search_index][str_index]:
                        tmp[str_index] = 0

            # tmpに1つでも1があるかつ全てのスロットにコマを置いている 
            if 1 in tmp and has_empty_slot is False:
                return (2, i, tmp)

        if '' not in FieldInfo.field_status:
            return (1, -1, [])
    
        return (0, -1, [])
          

    def judgeGameOver(self, _current_player):
        game_over_info = self.gameIsOver(_current_player)
        game_over_type = game_over_info[0]

        if game_over_type == GameOverType.WIN:
            self.view.dispGameIsOver(_current_player.name)
            self.view.drawField(game_over_info[1:3])
        elif game_over_type == GameOverType.DRAW:
            self.view.dispGameIsDraw()

        return game_over_type


    def qLearning(self):
        self.q_npc_0 = QNPC("0O0")
        self.q_npc_1 = QNPC("1l1")

        current_player = self.q_npc_1
        given_piece = current_player.selectRandomPiece()
        for i in range(16):
            if i%2 == Turn.PLAYER:
                current_player = self.q_npc_0
                (_, vec, selected_piece) = current_player.selectNextAction(given_piece)
            else:
                current_player = self.q_npc_1
                (_, vec, given_piece) = current_player.selectNextAction(selected_piece)

            game_over_type = self.judgeGameOver(current_player)
            if game_over_type != GameOverType.NOTOVER:
                current_player.updateNextQValue(vec, game_over_type)
                break


    def main(self, _npc_type=NPCType.QNPC):
        if _npc_type == NPCType.QNPC:
            self.npc = QNPC("QNPC")
        else:
            self.npc = NPC("NPC")

        current_player = self.npc
        given_piece = current_player.selectRandomPiece()
        for i in range(16):
            if i%2 == Turn.PLAYER:
                current_player = self.player
                # Playerがスロット選択
                self.view.drawField()
                self.view.dispReceivedPieceInstruction(given_piece)
                while(True):
                    self.view.dispSelectSlotInstruction()
                    player_input = input()
                    selected_pos = sorted(player_input)
            
                    if len(selected_pos) == 0:
                        idx = current_player.selectRandomSlotIndex()
                    elif len(selected_pos) != 2:
                        continue
                    elif (selected_pos[0] in [str(i) for i in range(1, 1+4)] 
                        and selected_pos[1].upper() in [chr(i) for i in range(65, 65+4)]):
                        idx = (int(selected_pos[0]) - 1) * 4 + [chr(i) for i in range(65, 65+4)].index(selected_pos[1].upper())
                    else:
                        continue
                    
                    if FieldInfo.selectedSlotIsEmpty(idx):
                        current_player.selectSlot(given_piece, idx)
                        break
                    else:
                        self.view.dispSelectSlotWarning()

                self.view.dispSelectedSlotInfo(current_player.name, idx)
                self.view.drawField()

                if self.judgeGameOver(current_player) != GameOverType.NOTOVER:
                    break

                # Playerがコマ選択
                self.view.dispAvailablePiecesInfo()
                selected_piece = ''
                while(True):
                    self.view.dispSelectPieceInstruction()
                    selected_piece_id = input()
                    if selected_piece_id == '':
                        selected_piece = current_player.selectRandomPiece()
                        break
                    else:
                        try:
                            selected_piece_id = int(selected_piece_id) - 1
                        except ValueError:
                            continue

                    if 0 <= selected_piece_id < len(FieldInfo.available_pieces):
                        selected_piece = current_player.selectPiece(selected_piece_id)
                        break
                self.view.dispSelectedPieceInfo(selected_piece)

            else:
                current_player = self.npc
                (idx, _, given_piece) = self.npc.selectNextAction(selected_piece)
                self.view.dispSelectedSlotInfo(current_player.name, idx)
                if self.judgeGameOver(current_player) != GameOverType.NOTOVER:
                    break

      
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'QUARTOで遊ぶことができます')
    parser.add_argument('--hard', action = 'store_true', help = 'hard modeで遊ぶことができます')
    parser.add_argument('-q', '--qlearn', action = 'store_true', help = 'Q学習した相手と対戦できます')
    args = parser.parse_args()

    if args.hard:
        qa = Qarto(Difficulty.HARD)
    else:
        qa = Qarto(Difficulty.NORMAL)

    if args.qlearn:
        qa.main(NPCType.QNPC)
    else:
        qa.main(NPCType.NPC)
