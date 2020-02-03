import random
import sys
import textwrap
from enum import Enum, IntEnum
from Player import Player, NPC
from GameInfo import FieldInfo
from View import View


class Difficulty(Enum):
    NORMAL = 0
    HARD = 1


class Turn(IntEnum):
    PLAYER = 0
    NPC = 1


class Qarto(object):
    def __init__(self, _game_mode=Difficulty.NORMAL):
        self.view = View()
        self.npc = NPC("Alice")
        self.player = Player("Bob")

        if _game_mode == Difficulty.HARD:
            FieldInfo.changeDifficulty
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
                self.view.dispGameIsOver(_current_player.name)
                self.view.drawField(i, tmp.index(1)) 
                return True

        if '' not in FieldInfo.field_status:
            self.view.dispGameIsDraw()
    
        return False
    

    def main(self):

        self.view.drawField()

        current_player = self.player
        for i in range(16):
            if i%2 == Turn.PLAYER:
                current_player = self.player

                # NPCがコマ選択
                selected_piece = self.npc.selectRandomPiece()
                self.view.dispReceivedPieceInstruction(selected_piece)

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
                        self.player.selectSlot(selected_piece, idx)
                        break
                    else:
                        self.view.dispSelectSlotWarning()

                self.view.dispSelectedSlotInfo(self.player.name, idx)

            else:
                current_player = self.npc

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

                # NPCがスロット選択
                idx = self.npc.selectRandomSlotIndex()
                self.npc.selectSlot(selected_piece, idx)
                self.view.dispSelectedSlotInfo(self.npc.name, idx)

            if self.gameIsOver(current_player):
                break
    
            self.view.drawField()


if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 2 and args[1].lower() == 'hard':
        qa = Qarto(Difficulty.HARD)
    else:
        qa = Qarto(Difficulty.NORMAL)

    qa.main()
