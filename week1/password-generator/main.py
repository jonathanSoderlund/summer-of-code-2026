from utils import generate_password

def get_user_input():
    length = int(input("Length: "))
    use_special = input("Include special chars? (y/n): ") == "y"
    return length, use_special

def main():
    length, use_special = get_user_input()
    password = generate_password(length, use_special)
    print(f"Generated password: {password}")

if __name__ == "__main__":
    main()