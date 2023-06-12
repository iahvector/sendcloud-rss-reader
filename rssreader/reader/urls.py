from django.urls import path, include
from rest_framework import routers

from reader.views import FeedsApi, ItemsApi

router = routers.DefaultRouter()
router.register(r'feeds', FeedsApi, basename='Feed')
router.register(r'items', ItemsApi, basename='Item')

urlpatterns = [
    path('', include(router.urls)),
]
