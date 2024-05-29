import hashlib

if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly. Please run the main script called um_members.py")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
