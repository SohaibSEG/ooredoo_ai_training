from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User


class AuthService:
    def register_user(self, db: Session, email: str, name: str, password: str) -> User:
        user = User(email=email, name=name, password_hash=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate(self, db: Session, email: str, password: str) -> User | None:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def create_tokens(self, user: User) -> tuple[str, str]:
        return create_access_token(str(user.id)), create_refresh_token(str(user.id))

    def refresh_access_token(self, refresh_token: str) -> str:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
        subject = payload.get("sub")
        return create_access_token(subject)
