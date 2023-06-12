from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from users.repositories import UsersRepository
from users.services import UsersService
from users.serializers import UserSerializer
from users.domain_models import User


class UsersApi(viewsets.ViewSet):
    permission_classes = [AllowAny,]

    users_repo = UsersRepository()
    users_service = UsersService(users_repo)

    @extend_schema(
        request=UserSerializer,
        responses={201: UserSerializer},
        operation_id='Sugn up'
    )
    def create(self, request):
        req_serializer = UserSerializer(data=request.data)
        if not req_serializer.is_valid():
            raise ValidationError(detail=req_serializer.errors)
        
        data = req_serializer.validated_data
        password = data['password']
        user = User(
            id=None,
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        user = self.users_service.signup(user, password)

        return Response(
            UserSerializer(user).data, status=status.HTTP_201_CREATED
        )
        