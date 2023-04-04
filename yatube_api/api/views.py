from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .permissions import IsAuthorOrReadOnly
from posts.models import Group, Post
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .serializers import CommentSerializer, GroupSerializer
from .serializers import PostSerializer, FollowSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied("Нельзя изменять этот контент")
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Нельзя удалять этот контент")
        return super().perform_destroy(instance)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthorOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        new_queryset = post.comments.all()
        return new_queryset

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)

    def perform_update(self, serializer):
        if serializer.instance.author == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied("Нельзя редактировать этот комментарий")

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied("Вы не можете удалить этот комментарий")


class FollowViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user__username', 'following__username',)

    def get_queryset(self):
        queryset = self.request.user.follower.all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
