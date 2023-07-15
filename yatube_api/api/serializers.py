from rest_framework import serializers

from posts.models import Comment, Follow, Group, Post, User


class UserSerializer(serializers.ModelSerializer):
    posts = serializers.SlugRelatedField(many=True, read_only=True,
                                         slug_field='text')

    class Meta:
        model = User
        fields = '__all__'
        ref_name = 'ReadOnlyUsers'


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True,
                                        slug_field='username')
    following = serializers.SlugRelatedField(queryset=User.objects.all(),
                                             slug_field='username')

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        if data['following'] == self.context['request'].user:
            raise serializers.ValidationError('Нельзя подписаться'
                                              ' на самого себя!')
        elif Follow.objects.filter(following=data['following']).exists():
            raise serializers.ValidationError('Вы уже подписаны'
                                              ' на этого автора!')
        return data


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    pub_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Post
        # Указал явно, чтобы порядок полей соответствовал документации.
        fields = ('id', 'author', 'text', 'pub_date', 'image', 'group')


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('created', 'post')
