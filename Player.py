import random
from abc import ABCMeta
from abc import abstractmethod
import Levenshtein
import pickle
from GameInfo import FieldInfo, QInfo

ALPHA = 0.3
GAMMA = 0.2
EPSILON = 0.3
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
    def selectSlot(self, _given_piece, _idx):
        FieldInfo.field_status[_idx] = _given_piece
    def selectPiece(self):
        pass


class QNPC(AbsPlayer):
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
            for selected_slot_idx in [i for i, e in enumerate(field_vec) if e == '`']:
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
                    for selected_piece in FieldInfo.available_pieces:
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


    def selectSlot(self, _given_piece, _idx):
        FieldInfo.field_status[_idx] = _given_piece
    def selectPiece(self, _selected_piece):
        pass
