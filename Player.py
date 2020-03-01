import random
import copy
from abc import ABCMeta
from abc import abstractmethod
import Levenshtein
import pickle
from GameInfo import FieldInfo, QInfo

ALPHA = 0.3
GAMMA = 0.2
EPSILON = 0.0
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


class Player(AbsPlayer):
    def selectSlot(self, _given_piece, _idx):
        FieldInfo.field_status[_idx] = _given_piece

    def selectPiece(self, _idx):
        selected_piece = FieldInfo.available_pieces[_idx]
        FieldInfo.available_pieces.remove(selected_piece)
        return selected_piece


class NPC(AbsPlayer):
    def selectSlot(self, _given_piece):
        idx = self.selectQuartoSlotIndex(_given_piece)
        if idx == -1: # どこに置いてもQUARTOになってしまう
            idx = self.selectRandomSlotIndex()
        FieldInfo.field_status[idx] = _given_piece
        return idx

    def selectPiece(self, _available_pieces):
        selected_piece = ''
        while(True):
            selected_piece = random.choice(_available_pieces)
            _available_pieces.remove(selected_piece)
            idx = self.selectQuartoSlotIndex(selected_piece)
            if idx == -1: # selected_pieceがQUARTOにならない
                FieldInfo.available_pieces.remove(selected_piece)
                break
            if len(_available_pieces) == 0:
                selected_piece = self.selectRandomPiece()
                break
        return selected_piece

    def selectQuartoSlotIndex(self, _given_piece):
        for i in range(len(FieldInfo.clear_patterns)): # 0~9 or 0~18
            tmp = [1] * 4
            empty_count = 0
            self.field_status = copy.deepcopy(FieldInfo.field_status)
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
    
    def selectNextAction(self, _given_piece):
        idx = self.selectSlot(_given_piece)
        selected_piece = self.selectPiece(copy.deepcopy(FieldInfo.available_pieces))
        return (idx, '', selected_piece)


class QNPC(NPC):
    def __init__(self, _name):
        super().__init__(_name)
        with open('QNPC_Dict.pickle', 'rb') as f:
            QInfo.q_values = pickle.load(f)

    def encodePiece(self, _piese):
        return (chr(ord('a')+int(_piese, 2)))

    # 現在のフィールドのベクトル化
    def encodeField(self):
        field_v = ''
        for status in FieldInfo.field_status:
            if status != '':
                field_v = field_v + self.encodePiece(status)
            else:
                field_v = field_v + (chr(ord('a')-1))
        return field_v

    def selectNextAction(self, _given_piece):
        if random.random() < EPSILON:
            tmp_field_vec  = self.encodeField()
            selected_slot_idx   = self.selectRandomSlotIndex()
            # 10000はダミー
            selected_piece = self.selectRandomPiece() if len(FieldInfo.available_pieces) != 0 else '10000'
            tmp_vec = tmp_field_vec[:selected_slot_idx] + self.encodePiece(_given_piece)\
                + tmp_field_vec[selected_slot_idx+1:] + self.encodePiece(selected_piece)

            if tmp_vec not in QInfo.q_values:
                QInfo.q_values[tmp_vec] = random.random()
            
            FieldInfo.field_status[selected_slot_idx] = _given_piece

            return (selected_slot_idx, tmp_vec, selected_piece)
        else:
            field_vec = self.encodeField()

            # 空いているインデックス一覧を取得，状態ベクトルに変換，最も高いQ値が得られる状態を選ぶ
            # 状態ベクトル:[0]-[15]->FieldInfo.field_status, [16]->selected_piece
            app_slot_info = ()
            max_v = 0.0

            can_win_slot_idx = self.selectQuartoSlotIndex(_given_piece)
            selected_slot_idx_list = []
            if can_win_slot_idx != -1:
                selected_slot_idx_list.append(can_win_slot_idx)
            else:
                selected_slot_idx_list = [i for i, e in enumerate(field_vec) if e == '`']

            for selected_slot_idx in selected_slot_idx_list:
                tmp_field_vec = field_vec[:selected_slot_idx] + self.encodePiece(_given_piece)\
                     + field_vec[selected_slot_idx+1:]

                if len(FieldInfo.available_pieces) == 0:
                    selected_piece = '10000'
                    tmp_vec = tmp_field_vec + self.encodePiece(selected_piece)

                    if tmp_vec not in QInfo.q_values:
                        QInfo.q_values[tmp_vec] = random.random()

                    if max_v < QInfo.q_values[tmp_vec]:
                        app_slot_info = (selected_slot_idx, tmp_vec, selected_piece)
                        max_v = QInfo.q_values[tmp_vec]

                else:
                    # QUARTOにならないコマの候補を抽出
                    copied_available_pieces = copy.deepcopy(FieldInfo.available_pieces)
                    not_next_quarto_pieces = []
                    while (len(copied_available_pieces) != 0):
                        random_selected_piece = random.choice(copied_available_pieces)
                        copied_available_pieces.remove(random_selected_piece)
                        quarto_slot_idx = self.selectQuartoSlotIndex(random_selected_piece)
                        if quarto_slot_idx == -1 or (quarto_slot_idx != -1 and len(not_next_quarto_pieces) == 0):
                            not_next_quarto_pieces.append(random_selected_piece)

                    for selected_piece in not_next_quarto_pieces:
                        tmp_vec = tmp_field_vec + self.encodePiece(selected_piece)

                        if tmp_vec not in QInfo.q_values:
                            QInfo.q_values[tmp_vec] = random.random()
                        
                        if max_v < QInfo.q_values[tmp_vec]:
                            app_slot_info = (selected_slot_idx, tmp_vec, selected_piece)
                            max_v = QInfo.q_values[tmp_vec]

            FieldInfo.field_status[app_slot_info[0]] = _given_piece

            if len(FieldInfo.available_pieces) != 0:
                FieldInfo.available_pieces.remove(app_slot_info[2])

            return app_slot_info
    

    def updateNextQValue(self, _field_vec, _result):
        old_qv = QInfo.q_values[_field_vec]
        if _result == 2:
            # 報酬は1000, 手数が小さいほど評価
            QInfo.q_values[_field_vec] = old_qv + ALPHA*(1000/(16-len(FieldInfo.available_pieces)) - old_qv)
        else:
            # 想定されるパターン全てを列挙
            next_states = [(vec, v) for vec, v in QInfo.q_values.items()
                            if Levenshtein.distance(_field_vec[0:16], vec[0:16]) == 2 and
                                _field_vec.count('`')-vec.count('`') >= 2]
            max_qv = max(next_states, key=lambda v: v[1])[1] if len(next_states) != 0 else random.random()
            if len(next_states) != 0:
                print(_field_vec+':', end='')
                print(max(next_states, key=lambda v: v[1]))

            QInfo.q_values[_field_vec] = old_qv + ALPHA*(GAMMA*max_qv - old_qv)
