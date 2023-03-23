import secrets
import string


def generate_salt():
    # Define the character set
    charset = string.ascii_letters + string.digits + "./"
    # Generate a random 16-byte salt
    salt = "".join(secrets.choice(charset) for _ in range(16)).encode("utf-8")
    return salt
