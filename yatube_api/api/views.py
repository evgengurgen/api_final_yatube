import datetime as dt

from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination

from posts.models import Follow, Group, Post
from .permissions import ReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)


class CreateListViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    pass


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, pub_date=dt.datetime.now())

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('У вас недостаточно прав'
                                   ' для выполнения данного действия.')
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('У вас недостаточно прав'
                                   ' для выполнения данного действия.')
        instance.delete()

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            return (ReadOnly(),)
        return super().get_permissions()


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            return (ReadOnly(),)
        return super().get_permissions()


class FollowViewSet(CreateListViewSet):
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post.comments

    def perform_create(self, serializer):
        get_object_or_404(Post, id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user,
                        created=dt.datetime.now(),
                        post_id=self.kwargs.get('post_id'))

    def perform_update(self, serializer):
        get_object_or_404(Post, id=self.kwargs.get('post_id'))
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('У вас недостаточно прав'
                                   ' для выполнения данного действия.')
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        get_object_or_404(Post, id=self.kwargs.get('post_id'))
        if instance.author != self.request.user:
            raise PermissionDenied('У вас недостаточно прав'
                                   ' для выполнения данного действия.')
        instance.delete()

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            return (ReadOnly(),)
        return super().get_permissions()
