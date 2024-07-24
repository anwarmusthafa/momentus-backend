from rest_framework import serializers
from .models import Post , Comment , Like

class PostSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    momentus_user_name = serializers.SerializerMethodField()
    user_profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def get_image_url(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_momentus_user_name(self, obj):
        return obj.user.momentus_user_name

    def get_user_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.user.profile_picture:
            return request.build_absolute_uri(obj.user.profile_picture.url)
        return None

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

class CommentSerializer(serializers.ModelSerializer):
    momentus_user_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'comment', 'created_at', 'updated_at', 'momentus_user_name', 'profile_picture']

    def get_momentus_user_name(self, obj):
        return obj.user.momentus_user_name

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.user.profile_picture:
            return request.build_absolute_uri(obj.user.profile_picture.url)
        return None

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']