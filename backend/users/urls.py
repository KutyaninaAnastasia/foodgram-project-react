from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, FollowApiView, ListFollowViewSet

app_name = 'users'

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('users/<int:user_id>/subscribe/',
         FollowApiView.as_view(),
         name='subscribe'),
    path('users/subscriptions/',
         ListFollowViewSet.as_view(),
         name='subscriptions'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]