import os
from base64 import b64encode, b64decode
import datetime
import secrets
from cryptography.fernet import Fernet
from hashlib import pbkdf2_hmac
from account.models import AuthToken, User
from util.checker import Checker


# returns the hashed data and the salt respectively in a tuple
def hash(data: str) -> tuple[str, str]:
    salt = os.urandom(16)
    hashed = pbkdf2_hmac("sha256", data.encode(), salt, 65536)
    return (b64encode(hashed).decode(), b64encode(salt).decode())


def hash_with_salt(data: str, salt: str) -> str:
    hashed = pbkdf2_hmac("sha256", data.encode(), b64decode(salt.encode()), 65536)
    return b64encode(hashed).decode()


# returns the encrypted data and the salt respectively in a tuple
def encrypt(data: str) -> tuple[bytes, bytes]:
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())

    return (key, encrypted)


# same as encrypt() but you provide the key
def encrypt_with_key(data: str, key: bytes) -> tuple[bytes, bytes]:
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())

    return (key, encrypted)


def decrypt(data: bytes, key: bytes) -> str:
    f = Fernet(key)
    decrypted = f.decrypt(data)

    return decrypted.decode()


# Add a user to the database
def register_user(user_data: dict):
    first_name = user_data["first_name"]
    last_name = user_data["last_name"]
    email = user_data["email"]
    password = user_data["password"]

    # check if user already exists by checking if email is already in use
    existing_user_query = User.users.filter(email=email)

    # TODO: should be returning forbidden instead
    if existing_user_query.count() > 0:
        return Checker(
            message="A user with that email already exists"
        )

    # contains the encrypted password and the salt respectively
    password_encrypted: tuple[str, str] = hash(password)

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        bio="",
        salt=password_encrypted[1],
        password=password_encrypted[0]
    )

    user.save()

    return Checker(
        success=True,
        message="Successfully Registered!"
    )


def login_user(user_data: dict) -> Checker:
    email = user_data["email"]
    password = user_data["password"]

    user_query = User.users.filter(email=email)

    if user_query.count() <= 0:
        print(f"no user found with email {email}")
        return Checker(
            message=f"no user found with email {email}",
        )

    stored_password = user_query[0].password
    password_rehashed = hash_with_salt(password, user_query[0].salt)

    if password_rehashed != stored_password:
        return Checker(
            message=f"password was incorrect for user {email}"
        )

    generated_token = create_auth_token(user_id=user_query[0], overwrite_token=True)

    if not generated_token:
        return Checker(
            message="token already exists"
        )

    return Checker(
        success=True,
        message="successfully logged in!",
        data={
            "token": generated_token
        }
    )


def validate_auth_token(auth_token: str | None, user_id: int):
    existing_token = AuthToken.tokens.filter(user_id=user_id)

    if existing_token.count() <= 0:
        return Checker(
            message="token does not exist"
        )

    if auth_token is None or user_id == -1:
        return Checker(
            message="Authentication failed"
        )

    token_rehashed = hash_with_salt(auth_token, existing_token[0].salt)

    if token_rehashed != existing_token[0].token:
        return Checker(
            message="token is invalid"
        )

    return Checker(
        success=True,
        message="token is valid"
    )


def logout_user(auth_token: str | None, user_id: int):
    validation = validate_auth_token(auth_token, user_id)

    if not validation.success:
        return validation

    existing_token = AuthToken.tokens.filter(user_id=user_id)
    existing_token[0].delete()

    return Checker(
        success=True,
        message="successfully logged out!",
        data={
            "success": True
        }
    )


def auth_login_user(auth_token: str | None, user_id: int):
    validation = validate_auth_token(auth_token, user_id)

    if not validation.success:
        return validation

    existing_token = AuthToken.tokens.filter(user_id=user_id)

    cur_date = datetime.datetime.now()
    if cur_date.timestamp() >= existing_token[0].expiration.timestamp():
        existing_token[0].delete()
        return Checker(
            message="token has expired"
        )

    user = User.users.get(id=user_id)

    return Checker(
        success=True,
        message="successfully logged in!",
        data={
            "success": True,
            "user_id": user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    )


def create_auth_token(user_id: User, **overwrite_token: bool) -> str | None:
    existing_token = AuthToken.tokens.filter(user_id=user_id)

    if overwrite_token:
        existing_token = existing_token.delete()
    else:
        if existing_token.count() > 0:
            print(f"user {user_id} already has an auth_token")
            return None

    generated_token = secrets.token_urlsafe(16)
    hashed_token = hash(generated_token)

    expiration = datetime.datetime.now() + datetime.timedelta(days=62)

    token = AuthToken(
        token=hashed_token[0],
        salt=hashed_token[1],
        expiration=expiration,
        user_id=user_id
    )

    token.save()

    return generated_token


def get_user_details(user_id: int):
    found_user = User.users.filter(id=user_id)

    if found_user.count() <= 0:
        return Checker(
            status=404,
            success=False,
            message="user not found"
        )

    details = {
        "id": user_id,
        "first_name": found_user[0].first_name,
        "last_name": found_user[0].last_name,
        "bio": found_user[0].bio,
        "email": found_user[0].email,
        # "date_created": found_user[0].date_created,
    }

    return Checker(
        status=200,
        success=True,
        message="user found",
        data=details
    )


# assumes that a user with user_id exists
def update_user_details(data: dict, user_id: int):
    user = User.users.get(id=user_id)
    if "bio" in data:
        user.bio = data["bio"]
    if "first_name" in data:
        user.first_name = data["first_name"]
    if "last_name" in data:
        user.last_name = data["last_name"]
    if "email" in data:
        user.email = data["email"]

    user.save()

    details = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "bio": user.bio,
        "email": user.email,
        # "date_created": user.date_created,
    }
    return Checker(
        success=True,
        message="user updated",
        data=details
    )
