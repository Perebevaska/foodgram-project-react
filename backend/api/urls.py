from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import sign_up


router_v1 = DefaultRouter()


#router_v1.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/users/', sign_up),
]