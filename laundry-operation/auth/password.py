from passlib.context import CryptContext
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if not isinstance(password, str):
        password = str(password)
    try:
        return pwd_context.hash(password)
    except ValueError:
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not isinstance(plain_password, str):
        plain_password = str(plain_password)
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        try:
            password_bytes = plain_password.encode("utf-8")
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            hash_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False
