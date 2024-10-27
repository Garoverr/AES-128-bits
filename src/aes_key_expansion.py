from .aes_tools import sbox, rcon

def string_to_byte_matrix(key):
    bytes_list = [int(key[i:i+2], 16) for i in range(0, len(key), 2)]
    matrix = [bytes_list[i:i+4] for i in range(0, len(bytes_list), 4)]
    return matrix


def get_column(matrix, col_index):
    return [row[col_index] for row in matrix]


def rot_word(column_block):
    return column_block[1:] + column_block[:1]


def sub_bytes_word(column_block):
    new_column = []
    for i in range(len(column_block)):
        new_column.append(sbox[column_block[i]])
    return new_column


def apply_rcon(column_block, wi_4, roundKeyIndex):
    return [(wi_4[i] ^ column_block[i] ^ rcon[i * 10 + roundKeyIndex]) for i in range(4)]


def xor(wi_1, wi_4):
    return [wi_1[i] ^ wi_4[i] for i in range(4)]


def key_expansion(key):
    key_bytes = [int(key[i:i+2], 16) for i in range(0, len(key), 2)]
    round_keys = [key_bytes]

    for i in range(10):
        last_column = [round_keys[i][j + 12] for j in range(4)]

        column_block = rot_word(last_column)
        column_block = sub_bytes_word(column_block)
        column_block = apply_rcon(column_block, round_keys[i][:4], i)

        new_key = column_block[:]
        for j in range(3):
            column_block = xor(column_block, round_keys[i][(j + 1) * 4:(j + 1) * 4 + 4])
            new_key.extend(column_block)

        round_keys.append(new_key)
        
    return round_keys


def generate_round_keys(round_keys):
    key_matrices = []
    for round_key in round_keys:
        matrix = [round_key[i:i+4] for i in range(0, len(round_key), 4)]
        key_matrices.append(matrix)
    return key_matrices 

