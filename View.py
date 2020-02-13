import textwrap
from GameInfo import FieldInfo

class View():
    field = textwrap.dedent("""
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
    piece_str = [['黒', '白'], ['高', '低'], ['円', '角'], ['穴', '平']]
    quarto_mark = ['　'] * len(FieldInfo.clear_patterns)
    piece_chars_on_slot = [['　'] * 4 for _ in range(16)]


    def dispTitleNormal(self):
        print('   *******      **     **       **       *******     **********     *******  ')
        print('  **/////**    /**    /**      ****     /**////**   /////**///     **/////** ')
        print(' **     //**   /**    /**     **//**    /**   /**       /**       **     //**')
        print('/**      /**   /**    /**    **  //**   /*******        /**      /**      /**')
        print('/**    **/**   /**    /**   **********  /**///**        /**      /**      /**')
        print('//**  // **    /**    /**  /**//////**  /**  //**       /**      //**     ** ')
        print(' //******* **  //*******   /**     /**  /**   //**      /**       //*******  ')
        print('  /////// //    ///////    //      //   //     //       //         ///////   ')


    def dispTitleHard(self):
        print('    .-.      wWw  wWw          ()_()  (o)__(o)     .-.    ')
        print('  c(O_O)c    (O)  (O)     /)   (O o)  (__  __)   c(O_O)c  ')
        print(" ,'.---.`,   / )  ( \   (o)(O)  |^_\    (  )    ,'.---.`, ")
        print('/ /|_|_|\ \ / /    \ \   //\\\   |(_))    )(    / /|_|_|\ \\')
        print('| \___.--.| | \____/ |  |(__)|  |  /    (  )   | \_____/ |')
        print("'. `---\) \ '. `--' .`  /,-. |  )|\\\\     )/    '. `---' .`")
        print("  `-...(_.'   `-..-'   -'   '' (/  \)   (        `-...-'  ")


    def drawField(self, _pattern_index=None, _pattern_type=None):
        for i in range(len(FieldInfo.field_status)):
            for j in range(4):
                if not FieldInfo.selectedSlotIsEmpty(i):
                    self.piece_chars_on_slot[i][j] = self.piece_str[j][int(FieldInfo.field_status[i][j])]
        if type(_pattern_type) == int and 0 <= _pattern_index <= 9:
            tmp = FieldInfo.field_status[FieldInfo.clear_patterns[_pattern_index][0]][_pattern_type]
            self.quarto_mark[_pattern_index] = self.piece_str[_pattern_type][int(tmp)]
        print(self.field.format(self.piece_chars_on_slot, self.quarto_mark))


    def dispReceivedPieceInstruction(self, _piece):
        print('\n{0[0]}{0[1]}\n{0[2]}{0[3]}\nを置いてください'
                .format([self.piece_str[i][int(_piece[i])] for i in range(4)]))


    def dispSelectSlotInstruction(self):
        print('\n置く場所を入力してください>>', end = '')


    def dispSelectSlotWarning(self):
        print('空いている場所に置いてください')


    def dispSelectedSlotInfo(self, _name, _selected_idx):
        print('\n' + _name + 'が{}{}にコマを置きました'
            .format(['Ａ', 'Ｂ', 'Ｃ', 'Ｄ'][_selected_idx % 4],
                    ['１', '２', '３', '４'][int(_selected_idx/4)]))


    def dispAvailablePiecesInfo(self):
        number_of_available_pieces = len(FieldInfo.available_pieces)
        for i in range(number_of_available_pieces):
            print('{:02} 　'.format(i + 1), end='')
        print()
        for i in range(number_of_available_pieces):
            print('{0[0]}{0[1]} '.format([self.piece_str[j][int(FieldInfo.available_pieces[i][j])] for j in range(4)]), end='')
        print()
        for i in range(number_of_available_pieces):
            print('{0[2]}{0[3]} '.format([self.piece_str[j][int(FieldInfo.available_pieces[i][j])] for j in range(4)]), end='')
        print('\nが残っています')

    
    def dispSelectPieceInstruction(self):
        print('\n渡すコマの番号を入力してください(1~{})>>'.format(len(FieldInfo.available_pieces)), end = '')
    

    def dispSelectedPieceInfo(self, _selected_piece):
        print('\n{0[0]}{0[1]}\n{0[2]}{0[3]}\nを渡します'
                .format([self.piece_str[i][int(_selected_piece[i])] for i in range(4)]))
            

    def dispGameIsDraw(self):
        print('引き分けです')
    

    def dispGameIsOver(self, _player_name):
        print('QUARTOです')   
        print(_player_name + 'の勝利!')
