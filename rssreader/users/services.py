from uuid import UUID
from users.domain_models import User
from users.repositories import UsersRepository

class UsersService:
    users_repo: UsersRepository

    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo
        
    def signup(self, user: User, password: str) -> User:
        return self.users_repo.create_user(user, password)
    
    def get_user(self, user_id: int) -> User:
        return self.users_repo.get_user(user_id)