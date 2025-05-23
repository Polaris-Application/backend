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
# from django.conf import settings
# import utils.email as email_handler
import jwt
# from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, logout
# from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from counseling.models import Pationt
import logging

logger = logging.getLogger(__name__)


class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        logger.warning( validated_data ) 
        email = self.normalize_email(validated_data["email"])
        role = User.TYPE_USER
        # Generate verification code
        verification_code = self.generate_verification_code()
        
        # Create user
        user = self.create_user(
            email=email,
            password=validated_data["password1"],
            verification_code=verification_code,
            role=role,
        )

        token = self.generate_verification_token(user)

        # # Send verification email
        # self.send_verification_email(
        #     user=user,
        #     verification_code=verification_code,
        #     token=token,
        # )
        # Prepare response data
        user_data = {
            "user": UserSerializer(user).data,
            "message": "User created successfully.",
            "code": verification_code,
            # "url": f"https://eniacgroup.ir/backend/accounts/activation_confirm/{token}/",
        }
        return Response(user_data, status=status.HTTP_201_CREATED)

    # Helper methods for better testability
    def normalize_email(self, email):
        """Normalize the email to lowercase."""
        return str.lower(email)

    # def generate_verification_code(self):
    #     """Generate a random verification code."""
    #     return str(random.randint(1000, 9999))

    def create_user(self, email, password, verification_code, role):
        """Create and return a user."""
        return User.objects.create(
            email=email,
            password=make_password(password),
            verification_code=verification_code,
            verification_tries_count=1,
            role=role,
        )

    def create_patient(self, user):
        """Create a Patient record for the user."""
        Pationt.objects.create(user=user)

    def generate_verification_token(self, user):
        """Generate an access token for the user."""
        return generate_tokens(user.id)["access"]

    # def send_verification_email(self, user, verification_code, token):
    #     """Send the verification email using a thread."""
    #     subject = "تایید ایمیل ثبت نام"
    #     show_text = (
    #         user.has_verification_tries_reset or user.verification_tries_count > 1
    #     )
    #     email_thread = EmailThread(
    #         email_handler,
    #         subject=subject,
    #         recipient_list=[user.email],
    #         verification_token=verification_code,
    #         registration_tries=user.verification_tries_count,
    #         show_text=show_text,
    #         token=token,
    #     )
    #     email_thread.start()



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
            {"message": "there is no user with this email"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RetrieveUserData(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        print(request.headers["Authorization"])
        if not hasattr(request, "user"):
            return Response(
                {"message": "request does not have proper authentication tokens"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email = str.lower(request.user.email)
        user = User.objects.filter(email__iexact=email)
        if not user.exists():
            return Response(
                {"message": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = user.first()
        data = {"user": UserSerializer(user).data}
        return Response(data=data, status=status.HTTP_200_OK)

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

