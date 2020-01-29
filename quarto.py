import random
import sys
import textwrap
from enum import Enum, IntEnum


class Difficulty(Enum):
    NORMAL = 0
    HARD = 1


class Turn(IntEnum):
    PLAYER = 0
    COM = 1


class Qarto(object):
    def __init__(self, game_mode=Difficulty.NORMAL):
        self.mapp=textwrap.dedent("""
        {1[8]}　｜Ａ{1[4]}｜Ｂ{1[5]}｜Ｃ{1[6]}｜Ｄ{1[7]}｜{1[9]}
        ＿＿丄＿＿丄＿＿丄＿＿丄＿＿」
        １　｜{0[0][0]}{0[0][1]}｜{0[1][0]}{0[1][1]}｜{0[2][0]}{0[2][1]}｜{0[3][0]}{0[3][1]}｜
        {1[0]}　｜{0[0][2]}{0[0][3]}｜{0[1][2]}{0[1][3]}｜{0[2][2]}{0[2][3]}｜{0[3][2]}{0[3][3]}｜
        ＿＿丄＿＿丄＿＿丄＿＿丄＿＿」
        ２　｜{0[4][0]}{0[4][1]}｜{0[5][0]}{0[5][1]}｜{0[6][0]}{0[6][1]}｜{0[7][0]}{0[7][1]}｜
        {1[1]}　｜{0[4][2]}{0[4][3]}｜{0[5][2]}{0[5][3]}｜{0[6][2]}{0[6][3]}｜{0[7][2]}{0[7][3]}｜
        ＿＿丄＿＿丄＿＿丄＿＿丄＿＿」
        ３　｜{0[8][0]}{0[8][1]}｜{0[9][0]}{0[9][1]}｜{0[10][0]}{0[10][1]}｜{0[11][0]}{0[11][1]}｜
        {1[2]}　｜{0[8][2]}{0[8][3]}｜{0[9][2]}{0[9][3]}｜{0[10][2]}{0[10][3]}｜{0[11][2]}{0[11][3]}｜
        ＿＿丄＿＿丄＿＿丄＿＿丄＿＿」
        ４　｜{0[12][0]}{0[12][1]}｜{0[13][0]}{0[13][1]}｜{0[14][0]}{0[14][1]}｜{0[15][0]}{0[15][1]}｜
        {1[3]}　｜{0[12][2]}{0[12][3]}｜{0[13][2]}{0[13][3]}｜{0[14][2]}{0[14][3]}｜{0[15][2]}{0[15][3]}｜
        ＿＿丄＿＿丄＿＿丄＿＿丄＿＿」
        """)
        self.search=[
            [0,1,2,3], [4,5,6,7], [8,9,10,11], [12,13,14,15], [0,4,8,12], 
            [1,5,9,13], [2,6,10,14], [3,7,11,15], [0,5,10,15], [3,6,9,12]
            ]

        if game_mode == Difficulty.HARD:
            self.search[len(self.search):len(self.search)] = [
                [0,1,4,5], [1,2,5,6], [2,3,6,7], [4,5,8,9], [5,6,9,10], 
                [6,7,10,11], [8,9,12,13], [9,10,13,14],[10,11,14,15]
            ]
        
        self.maplist = [''] * 16
        self.mapstr = [['　'] * 4 for _ in range(16)]
        self.piece = [format(i, '04b') for i in range(16)] #0000~1111
        self.piecestr = [['黒', '白'], ['高', '低'], ['円', '角'], ['有', '無']]
        self.quarto_mark = ['　'] * len(self.search)

    
    '''
    マップを描写します
    search_index = 0 ~ len(self.search)
    str_index_list = 0 ~ 3
    '''
    def draw_map(self, search_index=None, str_index_list=None):
        for i in range(len(self.maplist)):
            for j in range(4):
                if self.maplist[i] != '':
                    self.mapstr[i][j] = self.piecestr[j][int(self.maplist[i][j])]
    
        if type(search_index) == int:
            tmp = self.maplist[self.search[search_index][0]][str_index_list]
            self.quarto_mark[search_index] = self.piecestr[str_index_list][int(tmp)]
        
        print(self.mapp.format(self.mapstr, self.quarto_mark))
    

    ''' 利用可能なランダムなマスのインデックスを選ぶ '''
    def select_random_available_square_index(self):
        while(True):
            selected_index = random.randrange(len(self.maplist))
            if self.maplist[selected_index] == '': #0~15
                break
        return selected_index
    

    '''playerがコマを置きます'''
    def put_piece_by_player(self, choiced_piece):
        while(True):
            posi = sorted(input('\n置く場所を入力してください>>'))
    
            if posi == '':
                selected_index = self.select_random_available_square_index() #0~15
            elif len(posi) != 2:
                continue

            if (posi[0] in [str(i) for i in range(1, 1+4)] 
                and posi[1].upper() in [chr(i) for i in range(65, 65+4)]):
                selected_index = (int(posi[0]) - 1) * 4 + [chr(i) for i in range(65, 65+4)].index(posi[1].upper())
            else:
                continue
            
            if self.maplist[selected_index] == '':
                self.maplist[selected_index] = choiced_piece
                break
            else:
                print('空いている場所に置いてください')
    
        print('\nplayerが{}{}にコマを置きました'
            .format(['Ａ', 'Ｂ', 'Ｃ', 'Ｄ'][selected_index % 4],
                    ['１', '２', '３', '４'][int(selected_index/4)]))        


    '''comがコマを置きます'''
    def put_piece_by_com(self, choiced_piece):
        selected_index = self.select_random_available_square_index()
        self.maplist[selected_index] = choiced_piece
        
        print('\ncomが{}{}にコマを置きました'
            .format(['Ａ', 'Ｂ', 'Ｃ', 'Ｄ'][selected_index % 4],
                    ['１', '２', '３', '４'][int(selected_index/4)]))
    

    '''playerがcomにコマを渡します'''
    def give_piece_to_com(self):
        for i in range(len(self.piece)):
            print('{0[0]}{0[1]} '.format([self.piecestr[j][int(self.piece[i][j])] for j in range(4)]), end='')
        print()
        for i in range(len(self.piece)):
            print('{0[2]}{0[3]} '.format([self.piecestr[j][int(self.piece[i][j])] for j in range(4)]), end='')
        print('\nが残っています')
        
        while(True):
            num = input('\n渡すコマの番号を入力してください(1~{})>>'.format(len(self.piece)))
    
            if num == '':
                num = random.randrange(len(self.piece)) + 1
    
            try:
                num = int(num) - 1
            except:
                continue
            
            if 0 <= num <= len(self.piece) - 1:
                break
        
        player = self.piece[num]
        self.piece.remove(player)
        print('\n{0[0]}{0[1]}\n{0[2]}{0[3]}\nを渡します'
                .format([self.piecestr[i][int(player[i])] for i in range(4)]))
        
        return player

    
    '''comがplayerにコマを渡します'''
    def give_piece_to_player(self):
        com = random.choice(self.piece)
        self.piece.remove(com)
        print('{0[0]}{0[1]}\n{0[2]}{0[3]}\nを置いてください'
                .format([self.piecestr[i][int(com[i])] for i in range(4)]))
        
        return com

    
    def finish(self, _maplist):
        for i in range(len(self.search)): # 0~9 or 0~18
            tmp = [1] * 4
            empty = False
            for self.search_index in self.search[i]: #ex)[0, 4, 8, 12]
                if _maplist[self.search_index] == '':
                    empty = True
                    break
    
                for str_index in [x for x, y in enumerate(tmp) if y == 1]: # tmpが1のindexだけ調べる
                    if _maplist[self.search[i][0]][str_index] != _maplist[self.search_index][str_index]:
                        tmp[str_index] = 0
                
            if 1 in tmp and empty is False: # tmpに1つでも1がある
                print("quartoです")   
                self.draw_map(i, tmp.index(1)) 
                return True
    
        return False
    

    def main(self):
        self.draw_map()
        for i in range(16):
            if i % 2 == Turn.PLAYER:
                choiced_piece = self.give_piece_to_player()
                self.put_piece_by_player(choiced_piece)
            else:
                choiced_piece = self.give_piece_to_com()
                self.put_piece_by_com(choiced_piece)
                
            if self.finish(self.maplist):
                break
    
            self.draw_map()


if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 2 and args[1].lower() == 'hard':
        print('hard mode')
        qa = Qarto(Difficulty.HARD)
    else:
        print('nomal mode')
        qa = Qarto(Difficulty.NORMAL)

    qa.main()
