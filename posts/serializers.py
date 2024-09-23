from rest_framework import serializers
from .models import Post , Comment , Like

class PostSerializer(serializers.ModelSerializer):
    momentus_user_name = serializers.SerializerMethodField()
    user_profile_picture = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'caption', 'image', 'created_at', 'momentus_user_name', 'user_profile_picture', 'like_count', 'comment_count']

    def get_momentus_user_name(self, obj):
        return obj.user.momentus_user_name

    def get_user_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.user.profile_picture:
            return request.build_absolute_uri(obj.user.profile_picture.url)
        return None

    def get_like_count(self, obj):
        # Now we can directly use the related_name 'likes'
        return obj.likes.count()

    def get_comment_count(self, obj):
        # Now we can directly use the related_name 'comments'
        return obj.comments.count()

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    momentus_user_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    commented_by = serializers.SerializerMethodField()
    comment_post_user_id = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'comment', 'parent', 'created_at','momentus_user_name', 'profile_picture', 'commented_by','comment_post_user_id', 'replies']

    def get_momentus_user_name(self, obj):
        return obj.user.momentus_user_name

    def get_commented_by(self, obj):
        return obj.user.id

    def get_comment_post_user_id(self, obj):
        return obj.post.user.id

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.user.profile_picture:
            return request.build_absolute_uri(obj.user.profile_picture.url)
        return None

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']