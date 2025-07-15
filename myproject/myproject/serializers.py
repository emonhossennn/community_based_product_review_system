from rest_framework import serializers
from .models import Product, Comment


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    time_ago = serializers.CharField(source='get_time_ago', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'product', 'user', 'username', 'content', 'is_approved', 'created_at', 'time_ago']
        read_only_fields = ['user', 'is_approved', 'created_at', 'time_ago']

    def create(self, validated_data):
        # Automatically set the user to the current authenticated user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['product', 'content']

    def create(self, validated_data):
        # Automatically set the user to the current authenticated user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommentApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['is_approved']
