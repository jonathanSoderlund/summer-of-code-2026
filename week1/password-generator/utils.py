import random
import string

def generate_password(length, use_special):
    characters = string.ascii_letters + string.digits
    
    if use_special:
        characters += string.punctuation

    return "".join(random.choice(characters) for _ in range(length))