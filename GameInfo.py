class FieldInfo():
    field_status = []
    available_pieces = []

    clear_patterns = [
        [0,1,2,3], [4,5,6,7], [8,9,10,11], [12,13,14,15], [0,4,8,12], 
        [1,5,9,13], [2,6,10,14], [3,7,11,15], [0,5,10,15], [3,6,9,12]
        ]

    @staticmethod
    def resetFieldParams():
        FieldInfo.field_status = [''] * 16
        FieldInfo.available_pieces = [format(i, '04b') for i in range(16)] #0000~1111

    @staticmethod
    def selectedSlotIsEmpty(_index):
        return True if FieldInfo.field_status[_index] == '' else False
    
    @staticmethod
    def changeDifficulty():
        FieldInfo.clear_patterns.extend([
                [0,1,4,5], [1,2,5,6], [2,3,6,7], [4,5,8,9], [5,6,9,10], 
                [6,7,10,11], [8,9,12,13], [9,10,13,14],[10,11,14,15]
            ])
