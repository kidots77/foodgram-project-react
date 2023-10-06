from rest_framework import routers
from django.urls import include, path

from api.views import IngredientsViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register(
    'ingredients',
    IngredientsViewSet,
    basename='ingredients'
)

urlpatterns = [
    path('', include(router.urls))
]