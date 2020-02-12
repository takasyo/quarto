import random
from abc import ABCMeta
from abc import abstractmethod
from GameInfo import FieldInfo

SLOT_ALPHA = 0.1
SLOT_GAMMA = 0.9
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
    slot_q_values = {}

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

    def selectNextSlot(self, _given_piece):
        if random.random() < EPSILON:
            tmp_field_vec = self.encodeField()
            selected_idx = self.selectRandomSlotIndex()
            tmp_field_vec = tmp_field_vec[:selected_idx] + self.encodePiece(_given_piece) + tmp_field_vec[selected_idx+1:]

            if tmp_field_vec not in self.slot_q_values:
                self.slot_q_values[tmp_field_vec] = random.random()
            
            FieldInfo.field_status[selected_idx] = _given_piece

            return (selected_idx, tmp_field_vec)
        else:
            field_vec = self.encodeField()

            # 空いているインデックス一覧を取得，状態ベクトルに変換，最も高いQ値が得られる状態を選ぶ
            app_slot_info = ()
            max_v = 0.0
            for available_slot_idx in [i for i, e in enumerate(field_vec) if e == '`']:
                tmp_field_vec = field_vec[:available_slot_idx] + self.encodePiece(_given_piece) + field_vec[available_slot_idx+1:]

                if tmp_field_vec not in self.slot_q_values:
                    self.slot_q_values[tmp_field_vec] = random.random()
                
                if max_v < self.slot_q_values[tmp_field_vec]:
                    app_slot_info = (available_slot_idx, tmp_field_vec)
                    max_v = self.slot_q_values[tmp_field_vec]

            FieldInfo.field_status[app_slot_info[0]] = _given_piece

            return app_slot_info
    
    def debugSlotQValues(self):
        for item in self.slot_q_values.items():
            print(item)


    def updateNextSlotQValue(self, _field_vec, _game_is_over):
        old_qv = self.slot_q_values[_field_vec]
        if _game_is_over:
            # 報酬は1000
            self.slot_q_values[_field_vec] = old_qv + SLOT_ALPHA*(1000 - old_qv)
        else:
            # 相手の選択するコマが不明であるため今回のスロット中の最高期待値を学習
            self.slot_q_values[_field_vec] = old_qv + SLOT_ALPHA*(SLOT_GAMMA*old_qv - old_qv)


    def selectSlot(self, _given_piece, _idx):
        FieldInfo.field_status[_idx] = _given_piece
    def selectPiece(self, _idx):
        pass