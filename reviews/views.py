from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book, Review
from .serializers import (
    RegisterSerializer,
    BookSerializer,
    ReviewSerializer
)
from .permissions import IsOwnerOrReadOnly


# Register User
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


# Change Password
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect"},
                status=400
            )
        if len(new_password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters"},
                status=400
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully"}
        )


# Books List + Create
class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]

        return [permissions.AllowAny()]


# Book Detail
class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [permissions.IsAdminUser()]

        return [permissions.AllowAny()]


# Reviews List + Create
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        book_id = self.kwargs['book_id']

        return Review.objects.filter(book_id=book_id)

    def perform_create(self, serializer):
        book_id = self.kwargs['book_id']
        book = Book.objects.get(id=book_id)

        serializer.save(
            user=self.request.user,
            book=book
        )

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]


# Review Update/Delete
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrReadOnly
    ]


from django.shortcuts import render

# Create your views here.
