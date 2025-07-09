# accounts/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .serializers import UserRegistrationSerializer, UserSerializer
from ecommerce_project.permissions import IsModerator

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # ← Usa permission standard

    def get_object(self):
        return self.request.user


class UserManagementView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # ← Per ora usa questa, poi modificherai

class UserBanUnbanView(generics.UpdateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsModerator]

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        # opzionale: blocca self-ban
        if user == request.user:
            return Response({'detail': "Non puoi bannare te stesso."},
                            status=status.HTTP_400_BAD_REQUEST)

        flag = request.data.get('is_banned')
        if flag is None:
            return Response({'detail': "Devi inviare il flag 'is_banned'."},
                            status=status.HTTP_400_BAD_REQUEST)

        user.is_banned = flag
        user.save()
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)