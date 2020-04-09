import random
import copy
import Levenshtein
import pickle
import itertools
from abc import ABCMeta, abstractmethod
from GameInfo import FieldInfo, QInfo

ALPHA = 0.3
GAMMA = 0.2
EPSILON = 0.0
WIN = 5
REACH = 2

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
    def __init__(self, _name, _npc_turn):
        super().__init__(_name)
        self.npc_turn = _npc_turn

    def selectSlot(self, _given_piece):
        idx = self.selectQuartoSlotIndex(_given_piece, FieldInfo.field_status)
        if idx == -1:
            idx = self.selectRandomSlotIndex()
        FieldInfo.field_status[idx] = _given_piece
        return idx

    def selectQuartoSlotIndex(self, _given_piece, _field_status):
        for i in range(len(FieldInfo.clear_patterns)): # 0~9 or 0~18
            tmp = [1] * 4
            empty_count = 0
            field_status = copy.deepcopy(_field_status)
            for search_index in FieldInfo.clear_patterns[i]: #ex)FieldInfo.clear_patterns[i]=[0, 4, 8, 12]
                if field_status[search_index] == '':
                    if empty_count == 0: # empty slotが1つ目
                        field_status[search_index] = _given_piece
                        quarto_slot_index = search_index
                        empty_count = 1
                    else:                # empty slotが2つ目以降
                        empty_count = 2
                        break
    
                for str_index in [x for x, y in enumerate(tmp) if y == 1]: 
                    # tmpが1のindexだけ調べる
                    if field_status[FieldInfo.clear_patterns[i][0]][str_index] != field_status[search_index][str_index]:
                        tmp[str_index] = 0

            # tmpに1つでも1があるかつ全てのスロットにコマを置いている
            if 1 in tmp and empty_count == 1:
                return quarto_slot_index
        
        return -1

    def selectPiece(self, _available_pieces):
        selected_piece = ''
        if len(_available_pieces) != 0:
            while(True):
                selected_piece = random.choice(_available_pieces)
                _available_pieces.remove(selected_piece)
                idx = self.selectQuartoSlotIndex(selected_piece, FieldInfo.field_status)
                if idx == -1: # selected_pieceがQUARTOにならない
                    FieldInfo.available_pieces.remove(selected_piece)
                    break
                if len(_available_pieces) == 0:
                    selected_piece = self.selectRandomPiece()
                    break
        return selected_piece
    
    def selectNextAction(self, _given_piece, _turn):
        idx = self.selectQuartoSlotIndex(_given_piece, FieldInfo.field_status)
        field_status = copy.deepcopy(FieldInfo.field_status)
        available_pieces = copy.deepcopy(FieldInfo.available_pieces)

        if idx == -1 and _turn > 5:
            idx, selected_piece, _ = self.minimax(_given_piece, available_pieces, field_status, _turn)
            FieldInfo.field_status[idx] = _given_piece
            if selected_piece != '':
                FieldInfo.available_pieces.remove(selected_piece)
            print(f'\nminimaxの結果，{idx}に置く{selected_piece}を渡すがベストでした')
        else:
            idx = self.selectSlot(_given_piece)
            selected_piece = self.selectPiece(available_pieces)

        return (idx, '', selected_piece)

    def gameIsOver(self, _field_status):
        """
        :return: GameOverType
        """
        for i in range(len(FieldInfo.clear_patterns)): # 0~9 or 0~18
            tmp = [1] * 4
            has_empty_slot = False
            for search_index in FieldInfo.clear_patterns[i]: #ex)[0, 4, 8, 12]
                if _field_status[search_index] == '':
                    has_empty_slot = True
                    break
    
                for str_index in [x for x, y in enumerate(tmp) if y == 1]: 
                    # tmpが1のindexだけ調べる
                    if _field_status[FieldInfo.clear_patterns[i][0]][str_index] != _field_status[search_index][str_index]:
                        tmp[str_index] = 0

            # tmpに1つでも1があるかつ全てのスロットにコマを置いている 
            if 1 in tmp and has_empty_slot is False:
                return 2

        if '' not in _field_status:
            return 1
    
        return 0

    def calc_score(self, _field_status, _turn):
        score = 0
        for i in range(len(FieldInfo.clear_patterns)): # 0~9 or 0~18
            tmp = [1] * 4
            empty_count = 0
            empty_index = -1
            num = 0

            for search_index in FieldInfo.clear_patterns[i]: #ex)FieldInfo.clear_patterns[i]=[0, 4, 8, 12]
                if _field_status[search_index] == '':
                    if empty_count == 0: # empty slotが1つ目
                        empty_count += 1
                        empty_index = search_index
                    elif empty_count == 1: # empty slotが2つ目以降
                        break
    
                for str_index in [x for x, y in enumerate(tmp) if y == 1]:
                    if empty_index != -1 and _field_status[empty_index] == '':
                        num = 1
                        continue
                    # tmpが1のindexだけ調べる
                    if _field_status[FieldInfo.clear_patterns[i][num]][str_index] != _field_status[search_index][str_index]:
                        tmp[str_index] = 0

            # tmpに1つでも1があるかつ全てのスロットにコマを置いている
            if 1 in tmp and empty_count == 1: # リーチ
                score += REACH * (16-_turn) * 0.2
            if 1 in tmp and empty_count == 0: # QUARTO
                score += WIN * (16-_turn) * 0.25
        
        return score

    def minimax(self, _given_piece, _available_pieces, _field_status, _turn):
        if self.gameIsOver(_field_status) != 0:    
            return [-1, '', self.calc_score(_field_status, _turn)]

        if _turn % 2 == self.npc_turn:
            best = [-1, '', -9999]
        else:
            best = [-1, '', 9999]

        empty_field_slots = [x for x, y in enumerate(_field_status) if y == '']
        available_pieces = copy.deepcopy(_available_pieces)

        idx = self.selectQuartoSlotIndex(_given_piece, _field_status)
        if idx != -1:
            field_status = copy.deepcopy(_field_status)
            field_status[idx] = _given_piece
            return [idx, '', self.calc_score(field_status, _turn)]

        if len(available_pieces) == 0:
            tmp_piece = ''
            tmp_slot = _field_status.index('')
            _field_status[tmp_slot] = _given_piece
            _, _, score = self.minimax(tmp_piece, available_pieces, _field_status, _turn + 1)
            if _turn % 2 == self.npc_turn and score > best[2]:
                best[0] = tmp_slot
                best[1] = tmp_piece
                best[2] = score
            elif _turn % 2 != self.npc_turn and score < best[2]:
                best[0] = tmp_slot
                best[1] = tmp_piece
                best[2] = score

        for tmp_slot, tmp_piece in itertools.product(empty_field_slots, _available_pieces):
            _field_status[tmp_slot] = _given_piece # 渡されたコマを置く
            available_pieces.remove(tmp_piece) # 相手にコマを渡す
            
            _, _, score = self.minimax(tmp_piece, available_pieces, _field_status, _turn + 1)
            _field_status[tmp_slot] = '' # 置いたコマを戻す
            available_pieces.append(tmp_piece) # 渡したコマをもとに戻す

            if _turn % 2 == self.npc_turn and score > best[2]:
                best[0] = tmp_slot
                best[1] = tmp_piece
                best[2] = score
            elif _turn % 2 != self.npc_turn and score < best[2]:
                best[0] = tmp_slot
                best[1] = tmp_piece
                best[2] = score

        return best


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

    def selectNextAction(self, _given_piece, _turn):
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
            can_win_slot_idx = self.selectQuartoSlotIndex(_given_piece, FieldInfo.field_status)
            selected_slot_idx_list = []
            if can_win_slot_idx != -1:
                selected_slot_idx_list.append(can_win_slot_idx)
            else:
                selected_slot_idx_list = [i for i, e in enumerate(field_vec) if e == '`']

            app_slot_info = ()
            max_v = 0.0
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
                        quarto_slot_idx = self.selectQuartoSlotIndex(random_selected_piece, FieldInfo.field_status)
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