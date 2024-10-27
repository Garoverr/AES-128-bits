import sys

from .aes_parser import parse_args
from .aes_tools import xor_matrices, string_to_hex32, little_endian, text_to_hex_matrix, read_input_file, SBOX, INVERSE_SBOX
from .aes_key_expansion import key_expansion, generate_round_keys

class Aes:
    _is_mode_encrypt : bool = None
    _key = None
    _input_file : bool = None  
    _file = None
    _r_k_a = None # Round Keys Array
    
    def __init__(self, argv):
        self._is_mode_encrypt = argv[0]
        self._key = argv[1]
        self._input_file = argv[2]
        self._file = argv[3]
        self.init_key()
        self.key_expansion()
        if self.init_message() == 84:
            sys.exit(84)

    def key_expansion(self):
        n_key = little_endian(self._key)
        rka = key_expansion(n_key)
        self._r_k_a = generate_round_keys(rka)
        
        
    def encrypt(self):
        #Part_1
        state = text_to_hex_matrix(self._file)
        state = xor_matrices(state, self._r_k_a[0])
        
        #Part_2
        for i in range(1, 10):
            state = sub_bytes(state, rev=False)
            state = shift_raws(state)
            state = mix_columns(state, rev=False)
            state = xor_matrices(state, self._r_k_a[i])
            
        #Part_3
        state = sub_bytes(state, rev=False)
        state = shift_raws(state)
        state = xor_matrices(state, self._r_k_a[10])

        result = ''.join(f'{state[row][col]:02x}' for row in range(4) for col in range(4))

        result = little_endian(result)
        print(result)    
        return result
    
    
    def decrypt(self):
        #Part_1
        state = little_endian(self._file)
        state = string_to_matrix(state)
        state = xor_matrices(state, self._r_k_a[10])
        
        #Part_2
        for i in range(9, 0, -1):
             state = inv_shift_rows(state)
             state = sub_bytes(state, rev=True)
             state = xor_matrices(state, self._r_k_a[i])
             state = mix_columns(state, rev=True)

        #Part_3         
        state = inv_shift_rows(state)
        state = sub_bytes(state, rev=True)
        state = xor_matrices(state, self._r_k_a[0])
    
        result = ''.join(f'{state[row][col]:02x}' for row in range(4) for col in range(4))

        result_chars = ''.join(chr(int(result[i:i+2], 16)) for i in range(0, len(result), 2))
        print(result_chars)
        return result
    

    def init_key(self):
        n_key = ""
        if len(self._key) == 16:
            n_key = string_to_hex32(self._key)
        else:
            n_key = self._key
        self._key = n_key            
    
    
    def init_message(self):
        if self._input_file:
            self._file = read_input_file(self._file)
        else:
            self._file = sys.stdin.read().strip()
            
        if self._file is None:
            return 84
        
        if not self._is_mode_encrypt and len(self._file) != 32:
            print("Error: Decryption mode requires a 32-character long input")
            return 84
        if self._is_mode_encrypt and len(self._file) != 16:
            print("Error: Encryption mode requires a 16-character long input")
            return 84
        return 0
    
    
    def run(self) -> int:
        if self._is_mode_encrypt:
            self.encrypt()
        else:
            self.decrypt()
            


def run_my_aes(argv) -> int :
    parsed_argv = parse_args(argv)
    if parsed_argv is None:
        return 84
    aes = Aes(parsed_argv)
    return aes.run()


#-----------------aes_encrypt/decrypt_tools------------------#
#                                                            #
#------------------------------------------------------------#

def sub_bytes(state, rev=False):
    box = SBOX if not rev else INVERSE_SBOX
    for i in range(4):
        for j in range(4):
            byte = state[i][j]
            row = (byte >> 4) & 0x0F
            col = byte & 0x0F
            state[i][j] = box[row][col]
    return state


def shift_raws(state):
    for i in range(4):
        column = [state[row][i] for row in range(4)]
        column = column[i:] + column[:i]
        for row in range(4):
            state[row][i] = column[row]
    return state


def inv_shift_rows(state):
    result_matrix = [[0] * 4 for _ in range(4)]
    result_matrix[0][1], result_matrix[1][1], result_matrix[2][1], result_matrix[3][1] = state[3][1], state[0][1], state[1][1], state[2][1]
    result_matrix[0][2], result_matrix[1][2], result_matrix[2][2], result_matrix[3][2] = state[2][2], state[3][2], state[0][2], state[1][2]
    result_matrix[0][3], result_matrix[1][3], result_matrix[2][3], result_matrix[3][3] = state[1][3], state[2][3], state[3][3], state[0][3]
    result_matrix[0][0], result_matrix[1][0], result_matrix[2][0], result_matrix[3][0] = state[0][0], state[1][0], state[2][0], state[3][0]
    return result_matrix    


def galois_multiplication_by_2(byte):
    if byte & 0x80:
        return ((byte << 1) ^ 0x1B) & 0xFF
    else:
        return (byte << 1) & 0xFF


def galoisMult(byte, power):
    galois = 0
    for i in range(8):
        if power & 1:
            galois ^= byte
        shift = byte & 0x80
        byte <<= 1
        if shift:
            byte ^= 0x1b
        power >>= 1
    return galois % 256


def mix_single_column(column):
    """Use of Galois GF(2^8)"""
    b0, b1, b2, b3 = column
        
    c0 = galoisMult(b0, 2) ^ galoisMult(b1, 3) ^ b2 ^ b3
    c1 = b0 ^ galoisMult(b1, 2) ^ galoisMult(b2, 3) ^ b3
    c2 = b0 ^ b1 ^ galoisMult(b2, 2) ^ galoisMult(b3, 3)
    c3 = galoisMult(b0, 3) ^ b1 ^ b2 ^ galoisMult(b3, 2)
    return [c0, c1, c2, c3]


def rev_mix_single_column(column):
    """Use of Galois GF(2^8)"""
    b0, b1, b2, b3 = column
    
    c0 = galoisMult(b0, 14) ^ galoisMult(b1, 11) ^ galoisMult(b2, 13) ^ galoisMult(b3, 9)
    c1 = galoisMult(b0, 9) ^ galoisMult(b1, 14) ^ galoisMult(b2, 11) ^ galoisMult(b3, 13)
    c2 = galoisMult(b0, 13) ^ galoisMult(b1, 9) ^ galoisMult(b2, 14) ^ galoisMult(b3, 11)
    c3 = galoisMult(b0, 11) ^ galoisMult(b1, 13) ^ galoisMult(b2, 9) ^ galoisMult(b3, 14)
    return [c0, c1, c2, c3]


def galois_multiplication_by_14(byte):
    """Use of Galois GF(2^8) Only with the use of multiplication by 2"""
    return galois_multiplication_by_2(galois_multiplication_by_2(galois_multiplication_by_2(byte))) ^ galois_multiplication_by_2(galois_multiplication_by_2(byte)) ^ galois_multiplication_by_2(byte)   


def mix_columns(state, rev=False):
    mix_function = rev_mix_single_column if rev else mix_single_column
    
    column_1 = state[0][0], state[0][1], state[0][2], state[0][3]
    column_2 = state[1][0], state[1][1], state[1][2], state[1][3]
    column_3 = state[2][0], state[2][1], state[2][2], state[2][3]
    column_4 = state[3][0], state[3][1], state[3][2], state[3][3]
    
    n_column_1 = mix_function(column_1)
    n_column_2 = mix_function(column_2)
    n_column_3 = mix_function(column_3)
    n_column_4 = mix_function(column_4)
    
    for i in range(4):
        state[0][i] = n_column_1[i]
        state[1][i] = n_column_2[i]
        state[2][i] = n_column_3[i]
        state[3][i] = n_column_4[i]

    return state


def string_to_matrix(s):
    if len(s) != 32:
        raise ValueError("Input string must be 32 characters long")
    matrix = []
    for i in range(0, 32, 8):
        row = [int(s[j:j+2], 16) for j in range(i, i+8, 2)]
        matrix.append(row)
    return matrix
