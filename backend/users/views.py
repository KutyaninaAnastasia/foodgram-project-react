from djoser.views import UserViewSet
from rest_framework import permissions, status, views
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .models import CustomUser, Follow
from .serializers import CustomUserSerializer, FollowSerializer


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = CustomUserSerializer


class FollowApiView(views.APIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = FollowSerializer

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if request.user.id == user_id:
            return Response(
                {'error': 'Вы не можете подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(
                user=request.user,
                following_id=user_id).exists():
            return Response(
                {'error': 'Вы уже подписаны на пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(CustomUser, id=user_id)
        Follow.objects.create(
            user=request.user,
            following_id=user_id
        )
        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        get_object_or_404(CustomUser, id=user_id)
        subscription = Follow.objects.filter(
            user=request.user,
            following_id=user_id
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ListFollowViewSet(ListAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = FollowSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return CustomUser.objects.filter(following__user=self.request.user)
