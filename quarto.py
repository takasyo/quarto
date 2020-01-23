import random

mapp="""
　　｜Ａ　｜Ｂ　｜Ｃ　｜Ｄ　｜
＿＿丄＿＿丄＿＿丄＿＿丄＿＿」
１　｜{0[0][0]}{0[0][1]}｜{0[1][0]}{0[1][1]}｜{0[2][0]}{0[2][1]}｜{0[3][0]}{0[3][1]}｜
　　｜{0[0][2]}{0[0][3]}｜{0[1][2]}{0[1][3]}｜{0[2][2]}{0[2][3]}｜{0[3][2]}{0[3][3]}｜
＿＿丄＿＿丄＿＿丄＿＿丄＿＿」
２　｜{0[4][0]}{0[4][1]}｜{0[5][0]}{0[5][1]}｜{0[6][0]}{0[6][1]}｜{0[7][0]}{0[7][1]}｜
　　｜{0[4][2]}{0[4][3]}｜{0[5][2]}{0[5][3]}｜{0[6][2]}{0[6][3]}｜{0[7][2]}{0[7][3]}｜
＿＿丄＿＿丄＿＿丄＿＿丄＿＿」
３　｜{0[8][0]}{0[8][1]}｜{0[9][0]}{0[9][1]}｜{0[10][0]}{0[10][1]}｜{0[11][0]}{0[11][1]}｜
　　｜{0[8][2]}{0[8][3]}｜{0[9][2]}{0[9][3]}｜{0[10][2]}{0[10][3]}｜{0[11][2]}{0[11][3]}｜
＿＿丄＿＿丄＿＿丄＿＿丄＿＿」
４　｜{0[12][0]}{0[12][1]}｜{0[13][0]}{0[13][1]}｜{0[14][0]}{0[14][1]}｜{0[15][0]}{0[15][1]}｜
　　｜{0[12][2]}{0[12][3]}｜{0[13][2]}{0[13][3]}｜{0[14][2]}{0[14][3]}｜{0[15][2]}{0[15][3]}｜
＿＿丄＿＿丄＿＿丄＿＿丄＿＿」
"""
maplist = [''] * 16
mapstr = [["　"] * 4 for i in range(16)]
piece = [format(i, '04b') for i in range(16)]
piecestr = [['黒', '白'], ['高', '低'], ['円', '角'], ['有', '無']]

def draw_map():
    '''マップを描写します'''

    for i in range(len(maplist)):
        for j in range(4):
            if maplist[i] != '':
                mapstr[i][j]=piecestr[j][int(maplist[i][j])]

    print(mapp.format(mapstr))

def put_player(choiced):
    '''playerがコマを置きます'''

    while(True):
        posi = input('\n置く場所を入力してください>>')

        if posi == '':
            while(True):
                tmp = random.randrange(len(maplist)) #0~15
                if maplist[tmp] == '':
                    break

        elif len(posi) != 2:
            continue

        elif (posi[0] in [str(i) for i in range(1, 1+4)] 
            and posi[1].upper() in [chr(i) for i in range(65, 65+4)]):

            tmp = int(posi[0]) * 4 + [chr(i) for i in range(65, 65+4)].index(posi[1].upper()) - 4

        elif (posi[1] in [str(i) for i in range(1, 1+4)] 
            and posi[0].upper() in [chr(i) for i in range(65, 65+4)]):
            
            tmp = int(posi[1]) * 4 + [chr(i) for i in range(65, 65+4)].index(posi[0].upper()) - 4
        
        else:
            continue
        
        if maplist[tmp] == '':
            maplist[tmp] = choiced
            break
        else:
            print('空いている場所に置いてください')

    print('\nplayerが{}{}にコマを置きました'
        .format(['Ａ', 'Ｂ', 'Ｃ', 'Ｄ'][tmp%4], ['１', '２', '３', '４'][int(tmp/4)]))        

def put_com(choiced):
    '''comがコマを置きます'''

    while(True):
        tmp = random.randrange(len(maplist)) #0~15
        if maplist[tmp] == '':
            maplist[tmp] = choiced
            break
    
    print('\ncomが{}{}にコマを置きました'
        .format(['Ａ', 'Ｂ', 'Ｃ', 'Ｄ'][tmp%4], ['１', '２', '３', '４'][int(tmp/4)]))

def give_player():
    '''playerがcomにコマを渡します'''

    for i in range(len(piece)):
        print('{0[0]}{0[1]} '.format([piecestr[j][int(piece[i][j])] for j in range(4)]), end='')
    print()
    for i in range(len(piece)):
        print('{0[2]}{0[3]} '.format([piecestr[j][int(piece[i][j])] for j in range(4)]), end='')
    print('\nが残っています')
    
    while(True):
        num = input('\n渡すコマの番号を入力してください(1~{})>>'.format(len(piece)))

        if num == '':
            num = random.randrange(len(piece)) + 1

        try:
            num = int(num) - 1
        except:
            continue
        
        if 0 <= num <= len(piece) - 1:
            break
    
    player = piece[num]
    piece.remove(player)
    print('\n{0[0]}{0[1]}\n{0[2]}{0[3]}\nを渡します'
            .format([piecestr[i][int(player[i])] for i in range(4)]))
    
    return player

def give_com():
    '''comがplayerにコマを渡します'''
    
    com = random.choice(piece)
    piece.remove(com)
    print('{0[0]}{0[1]}\n{0[2]}{0[3]}\nを置いてください'
            .format([piecestr[i][int(com[i])] for i in range(4)]))
    
    return com

def finish():
    #draw_map()
    #print("quartoです")
    return True

def main():
    draw_map()

    for i in range(16):

        if i % 2 == 0:
            choiced = give_com()
            # put_com(choiced)
            put_player(choiced)
        else:
            choiced = give_player()
            put_com(choiced)
            
        #if finish():
        #    break

        draw_map()

if __name__ == "__main__":
    main()
