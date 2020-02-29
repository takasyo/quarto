import random
import sys
import textwrap
import argparse
import pickle
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

WINNING_COUNT = 0

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
            pass

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
          
    def qLearning(self):
        self.q_npc_0 = QNPC("0O0")
        self.q_npc_1 = QNPC("1l1")

        given_piece = self.q_npc_1.selectRandomPiece()
        for i in range(16):
            if i%2 == Turn.PLAYER:
                (idx, vec, selected_piece) = self.q_npc_0.selectNextAction(given_piece)
                game_over_info = self.gameIsOver(self.q_npc_0)
                game_over_type = game_over_info[0]
                if game_over_type == 2:
                    self.view.dispGameIsOver(self.q_npc_0.name)
                    self.view.drawField(game_over_info[1:3])
                    break
                self.q_npc_0.updateNextQValue(vec, game_over_type)

            else:
                (idx, vec, given_piece) = self.q_npc_1.selectNextAction(selected_piece)
                game_over_info = self.gameIsOver(self.q_npc_1)
                game_over_type = game_over_info[0]
                if game_over_type == 2:
                    self.view.dispGameIsOver(self.q_npc_1.name)
                    self.view.drawField(game_over_info[1:3])
                    break
                self.q_npc_1.updateNextQValue(vec, game_over_type)


    def main(self, _npc_type=NPCType.QNPC):
        if _npc_type == NPCType.QNPC:
            self.npc = QNPC("QNPC")
        else:
            self.npc = NPC("NPC")

        given_piece = self.npc.selectRandomPiece()
        for i in range(16):
            if i%2 == Turn.PLAYER:
                # Playerがスロット選択
                self.view.drawField()
                self.view.dispReceivedPieceInstruction(given_piece)
                while(True):
                    self.view.dispSelectSlotInstruction()
                    player_input = input()
                    selected_pos = sorted(player_input)
            
                    if len(selected_pos) == 0:
                        idx = self.player.selectRandomSlotIndex()
                    elif len(selected_pos) != 2:
                        continue
                    elif (selected_pos[0] in [str(i) for i in range(1, 1+4)] 
                        and selected_pos[1].upper() in [chr(i) for i in range(65, 65+4)]):
                        idx = (int(selected_pos[0]) - 1) * 4 + [chr(i) for i in range(65, 65+4)].index(selected_pos[1].upper())
                    else:
                        continue
                    
                    if FieldInfo.selectedSlotIsEmpty(idx):
                        self.player.selectSlot(given_piece, idx)
                        break
                    else:
                        self.view.dispSelectSlotWarning()

                self.view.dispSelectedSlotInfo(self.player.name, idx)
                self.view.drawField()

                game_over_info = self.gameIsOver(self.player)
                game_over_type = game_over_info[0]
                if game_over_type == 2:
                    self.view.dispGameIsOver(self.player.name)
                    self.view.drawField(game_over_info[1:3])
                    break
                elif game_over_type == 1:
                    self.view.dispGameIsDraw()
                    break

                # Playerがコマ選択
                self.view.dispAvailablePiecesInfo()
                selected_piece = ''
                while(True):
                    self.view.dispSelectPieceInstruction()
                    selected_piece_id = input()
                    if selected_piece_id == '':
                        selected_piece = self.player.selectRandomPiece()
                        break
                    else:
                        try:
                            selected_piece_id = int(selected_piece_id) - 1
                        except ValueError:
                            continue
                    if 0 <= selected_piece_id < len(FieldInfo.available_pieces):
                        selected_piece = self.player.selectPiece(selected_piece_id)
                        break
                self.view.dispSelectedPieceInfo(selected_piece)

            else:
                if _npc_type == NPCType.QNPC:
                    (idx, vec, given_piece) = self.npc.selectNextAction(selected_piece)

                    self.view.dispSelectedSlotInfo(self.npc.name, idx)

                    game_over_info = self.gameIsOver(self.npc)
                    game_over_type = game_over_info[0]
                    if game_over_type == 2:
                        self.view.dispGameIsOver(self.npc.name)
                        self.view.drawField(game_over_info[1:3])
                        break
                    elif game_over_type == 1:
                        self.view.dispGameIsDraw()
                        break
                
                else:
                    # NPCがスロット選択
                    idx = self.npc.selectSlot(selected_piece)
                    self.view.dispSelectedSlotInfo(self.npc.name, idx)

                    game_over_info = self.gameIsOver(self.npc)
                    game_over_type = game_over_info[0]
                    if game_over_type == 2:
                        self.view.dispGameIsOver(self.npc.name)
                        self.view.drawField(game_over_info[1:3])
                        break
                    elif game_over_type == 1:
                        self.view.dispGameIsDraw()
                        break

                    # NPCがコマ選択
                    given_piece = self.npc.selectPiece(FieldInfo.available_pieces[:])

      
if __name__ == "__main__":
    parser = argparse.ArgumentParser('QUARTOで遊ぶことができます')
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
