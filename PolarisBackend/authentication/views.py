from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView
from .serializers import *
from .models import User
from .utils import generate_tokens
import random
import jwt
from django.contrib.auth import login, logout
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        logger.warning(validated_data)

        role = User.TYPE_USER
        # Create user using manager
        user = User.objects.create_user(
            username=validated_data["username"],
            phone_number=validated_data["phone_number"],
            password=validated_data["password1"]
        )

        user.role = role
        user.save()

        token = self.generate_verification_token(user)

        user_data = {
            "user": UserSerializer(user).data,
            "message": "User created successfully.",
        }
        return Response(user_data, status=status.HTTP_201_CREATED)

    def generate_verification_token(self, user):
        """Generate an access token for the user."""
        return generate_tokens(user.id)["access"]


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        if user is not None:
            tokens = generate_tokens(user.id)
            # login(request, user)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return Response(
                {
                    "refresh": tokens["refresh"],
                    "access": tokens["access"],
                    "user": UserSerializer(user).data,
                }
            )
        return Response(
            {"message": "there is no user with this username"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RetrieveUserData(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    def get(self, request):
        username = request.query_params.get("username")
        
        if not username:
            return Response(
                {"message": "Username is required in query parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = self.get_user_by_username(username)

        if user is None:
            return Response(
                {"message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = {"user": UserSerializer(user).data}
        return Response(data=data, status=status.HTTP_200_OK)
    
    def get_user_by_username(self, username: str):
        try:
            return User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            return None


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                data={"detail": "Not logged in"}, status=status.HTTP_401_UNAUTHORIZED
            )       
        refresh_token = request.COOKIES.get("token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response(
                    data={"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                )
            response = Response(
                data={"detail": "Logged out successfully"}, status=status.HTTP_200_OK
            )
            response.delete_cookie("refresh_token")
            response.delete_cookie("access_token")
            response.cookies.pop("refresh_token", None)
            response.cookies.pop("access_token", None)
            return response

        logout(request)
        return Response(
            data={"detail": "Logged out successfully"}, status=status.HTTP_200_OK
        )

