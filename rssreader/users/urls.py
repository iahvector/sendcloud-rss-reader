from django.urls import path, include
from rest_framework import routers
from users.views import LoginApi, LogoutApi, LogoutAllApi, UsersApi

router = routers.DefaultRouter()
router.register(r'', UsersApi, basename='User')

urlpatterns = [
    path('login', LoginApi.as_view()),
    path('logout', LogoutApi.as_view()),
    path('logout-all', LogoutAllApi.as_view()),
    path('', include(router.urls))
]