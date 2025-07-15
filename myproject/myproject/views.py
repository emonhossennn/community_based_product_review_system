from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product, Comment
from .serializers import (
    ProductSerializer, 
    CommentSerializer, 
    CommentCreateSerializer,
    CommentApprovalSerializer
)


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can view products

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        Get all approved comments for a specific product.
        """
        product = self.get_object()
        comments = product.comments.filter(is_approved=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        elif self.action in ['approve', 'reject']:
            return CommentApprovalSerializer
        return CommentSerializer

    def get_queryset(self):
        """
        Filter comments based on user permissions:
        - Admin users see all comments
        - Regular users see only their own comments
        """
        if self.request.user.is_staff:
            return Comment.objects.all()
        return Comment.objects.filter(user=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """
        Approve a comment (admin only).
        """
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        """
        Reject a comment (admin only).
        """
        comment = self.get_object()
        comment.is_approved = False
        comment.save()
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def pending(self, request):
        """
        Get all pending comments for admin review.
        """
        pending_comments = Comment.objects.filter(is_approved=False)
        serializer = CommentSerializer(pending_comments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def approved(self, request):
        """
        Get all approved comments.
        """
        approved_comments = Comment.objects.filter(is_approved=True)
        serializer = CommentSerializer(approved_comments, many=True)
        return Response(serializer.data)