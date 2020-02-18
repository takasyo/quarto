import random
from abc import ABCMeta
from abc import abstractmethod
from GameInfo import FieldInfo

class AbsPlayer(metaclass = ABCMeta):
    def __init__(self, _name):
        self.name = _name
    @abstractmethod
    def selectSlot(self, _given_piece, _idx):
        pass
    @abstractmethod
    def selectPiece(self):
        pass

    def selectRandomPiece(self):
        selected_piece = random.choice(FieldInfo.available_pieces)
        FieldInfo.available_pieces.remove(selected_piece)
        return selected_piece

    def selectRandomSlotIndex(self):
        while(True):
            selected_idx = random.randrange(len(FieldInfo.field_status))
            if FieldInfo.selectedSlotIsEmpty(selected_idx): #0~15
                break
        return selected_idx

    def selectQuartoSlotIndex(self, _given_piece):
        for i in range(len(FieldInfo.clear_patterns)): # 0~9 or 0~18
            tmp = [1] * 4
            empty_count = 0
            self.field_status = FieldInfo.field_status[:] # copy
            for search_index in FieldInfo.clear_patterns[i]: #ex)FieldInfo.clear_patterns[i]=[0, 4, 8, 12]
                if FieldInfo.selectedSlotIsEmpty(search_index):
                    if empty_count == 0: # empty slotが1つ目
                        self.field_status[search_index] = _given_piece
                        quarto_slot_index = search_index
                        empty_count = 1
                    else:                # empty slotが2つ目以降
                        empty_count = 2
                        break
    
                for str_index in [x for x, y in enumerate(tmp) if y == 1]: 
                    # tmpが1のindexだけ調べる
                    if self.field_status[FieldInfo.clear_patterns[i][0]][str_index] != self.field_status[search_index][str_index]:
                        tmp[str_index] = 0

            # tmpに1つでも1があるかつ全てのスロットにコマを置いている 
            if 1 in tmp and empty_count == 1:
                return quarto_slot_index
        
        return -1


class Player(AbsPlayer):
    def selectSlot(self, _given_piece, _idx):
        FieldInfo.field_status[_idx] = _given_piece
    def selectPiece(self, _idx):
        selected_piece = FieldInfo.available_pieces[_idx]
        FieldInfo.available_pieces.remove(selected_piece)
        return selected_piece


class NPC(AbsPlayer):
    def selectSlot(self, _given_piece, _idx):
        FieldInfo.field_status[_idx] = _given_piece
    def selectPiece(self):
        pass
