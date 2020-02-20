import random
import sys
import textwrap
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

WINNING_COUNT = 0
class Qarto(object):
    def __init__(self, _game_mode=Difficulty.NORMAL):
        self.view = View()
        self.q_npc = QNPC("Alice")
        self.player = Player("Bob")

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
        self.q_npc_0 = QNPC("Adam")
        self.q_npc_1 = QNPC("Eve")
    
        given_piece = self.q_npc_1.selectRandomPiece()
        for i in range(16):
            if i%2 == Turn.PLAYER:
                (idx, vec, selected_piece) = self.q_npc_0.selectNextAction(given_piece)
                game_over_info = self.gameIsOver(self.q_npc_0)
                game_over_type = game_over_info[0]
                if game_over_type != 0:
                    break
                self.q_npc_0.updateNextQValue(vec, game_over_type)

            else:
                (idx, vec, given_piece) = self.q_npc_1.selectNextAction(selected_piece)
                result = self.gameIsOver(self.q_npc_1)
                game_over_info = self.gameIsOver(self.q_npc_1)
                game_over_type = game_over_info[0]
                if game_over_type != 0:
                    break
                self.q_npc_1.updateNextQValue(vec, game_over_type)


    def main(self):

        self.view.drawField()

        given_piece = self.q_npc.selectRandomPiece()
        self.view.dispReceivedPieceInstruction(given_piece)
        for i in range(16):
            if i%2 == Turn.PLAYER:
                # Playerがスロット選択
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
                    self.view.drawField(game_over_info[1], game_over_info[2].index(1)) 
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
                # NPCがスロット選択
                (idx, vec, given_piece) = self.q_npc.selectNextAction(selected_piece)
                game_over_info = self.gameIsOver(self.q_npc)

                self.view.dispSelectedSlotInfo(self.q_npc.name, idx)

                game_over_type = game_over_info[0]
                if game_over_type == 2:
                    self.view.dispGameIsOver(self.q_npc.name)
                    self.view.drawField(game_over_info[1], game_over_info[2].index(1)) 
                    break
                elif game_over_type == 1:
                    self.view.dispGameIsDraw()
                    break

                self.view.dispReceivedPieceInstruction(given_piece)
                self.view.drawField()



if __name__ == "__main__":
    args = sys.argv
    # for i in range(1, 10001):
    #     if len(args) >= 2 and args[1].lower() == 'hard':
    #         qa = Qarto(Difficulty.HARD)
    #     else:
    #         qa = Qarto(Difficulty.NORMAL)

    #     print(str(i) + ':' + str(len(QInfo.q_values)))
    #     qa.qLearning()
    
    #     if i%1000 == 01
    #         with open('QNPC_Dict.pickle', 'wb') as f:
    #             pickle.dump(QInfo.q_values, f)

    if len(args) >= 2 and args[1].lower() == 'hard':
        qa = Qarto(Difficulty.HARD)
    else:
        qa = Qarto(Difficulty.NORMAL)
    qa.main()
