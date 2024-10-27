valid_modes= {"-e", "-d"}


def check_key(key) -> bool:
    if len(key) == 16:
        if all(32 <= ord(char) <= 126 for char in key):
            return True
        else:
            print("Key must be a valid ASCII string of 16 characters")
            return False
    elif len(key) == 32:
        try:
            bytes.fromhex(key)
            return True
        except ValueError:
            print("Key must be a valid hexadecimal string of 32 characters")
            return False
    else:
        print("Key must be either 16 characters long (ASCII) or 32 characters long (hexadecimal)")
        return False


def parse_args(argv) -> list | None :
    e_mode = False
    key = None
    is_file = False
    file = None
    
    if len(argv) < 3:
        return None
    
    if not any(arg in valid_modes for arg in argv):
        print("Please provide at least one valid mode:")
        print("    '-e' for encryption")
        print("    '-d' for decryption")
        return None
    
    e_mode = True if "-e" in argv else False
   
    try:
        key_index = argv.index("-k") + 1
        if key_index >= len(argv):
            print("Please provide a key after '-k' flag")
            return None
        key = argv[key_index]
        if not check_key(key):
            return None
    except ValueError:
        print("Please provide a key using '-k' flag")
        return None
    
    if "-i" in argv:
        file_index = argv.index("-i") + 1
        if file_index >= len(argv):
            print("Please provide a file after '-i' flag")
            return None
        file = argv[file_index]
        is_file = True
    
    return [e_mode, key, is_file, file]