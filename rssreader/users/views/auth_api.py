from django.contrib.auth import login
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.serializers import AuthTokenSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from knox.views import (
    LoginView as KnoxLoginView,
    LogoutView as KnoxLogoutView,
    LogoutAllView as KnoxLogoutAllView
)


class LoginApi(KnoxLoginView):
    permission_classes = [AllowAny,]
    
    @extend_schema(
        request=AuthTokenSerializer,
        responses={200: AuthTokenSerializer},
        operation_id='Login'
    )
    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginApi, self).post(request, format=None)


@extend_schema_view(
    post=extend_schema(
        operation_id='Log out'
    )
)
class LogoutApi(KnoxLogoutView):
    pass


@extend_schema_view(
    post=extend_schema(
        operation_id='Log out all'
    )
)
class LogoutAllApi(KnoxLogoutAllView):
    pass