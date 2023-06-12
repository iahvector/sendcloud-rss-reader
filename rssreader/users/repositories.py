from uuid import UUID
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from users.domain_models import User as UserDM
from users.exceptions import UserAlreadyExistsException, UserNotFoundException


class UsersRepository:
    def _convert_user_to_domain_model(self, user_db: User) -> UserDM:
        return UserDM(
            id=user_db.id,
            username=user_db.username,
            email=user_db.email,
            first_name=user_db.first_name,
            last_name=user_db.last_name
        )
    
    def create_user(self, user: UserDM, password: str) -> UserDM:
        try:
            user_db = User.objects.create_user(
                username=user.username,
                email=user.email,
                password=password,
                first_name=user.first_name,
                last_name=user.last_name,
            )
        except IntegrityError:
            msg = f'User {user.email} alraedy exists'
            raise UserAlreadyExistsException(msg)
            
        return self._convert_user_to_domain_model(user_db)
    
    def get_user(self, user_id: int) -> UserDM:
        try:
            user_db = User.objects.get(id=user_id)
        except User.DoesNotExist as e:
            msg = f'User {user_id} not found'
            raise UserNotFoundException(msg)

        return self._convert_user_to_domain_model(user_db)
        