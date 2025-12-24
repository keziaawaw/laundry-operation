from typing import Optional, Dict
from auth.models import UserInDB
from datetime import datetime
import uuid

class UserRepository:
    def __init__(self):
        self.users: Dict[str, UserInDB] = {}
        self.users_by_username: Dict[str, str] = {}
        self.users_by_email: Dict[str, str] = {}
    
    def create_user(self, username: str, email: str, hashed_password: str, full_name: Optional[str] = None) -> UserInDB:
        if username in self.users_by_username:
            raise ValueError("Username already exists")
        if email in self.users_by_email:
            raise ValueError("Email already exists")
        
        user_id = str(uuid.uuid4())
        user = UserInDB(
            id=user_id,
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            created_at=datetime.utcnow()
        )
        
        self.users[user_id] = user
        self.users_by_username[username] = user_id
        self.users_by_email[email] = user_id
        
        return user
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        user_id = self.users_by_username.get(username)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user_id = self.users_by_email.get(email)
        if user_id:
            return self.users.get(user_id)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        return self.users.get(user_id)

user_repository = UserRepository()

