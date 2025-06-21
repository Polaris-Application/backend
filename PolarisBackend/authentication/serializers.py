from rest_framework import serializers
from django.contrib.auth import password_validation, get_user_model

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        validators=[password_validation.validate_password],
    )
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('phone_number', 'password1', 'password2')

    def validate_username(self, value):
        user_qs = User.objects.filter(username__iexact=value)
        if user_qs.exists():
            user = user_qs.first()
            if user.phone_number != self.initial_data.get('phone_number'):
                raise serializers.ValidationError("phone number already exists.")
        return str.lower(value)

    def validate(self, data):
        if data.get("password1") != data.get("password2"):
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        phone_number = validated_data["phone_number"]
        password = validated_data["password1"]
        return User.objects.create_user(phone_number=phone_number, password=password)

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(label="Phone Number")  
    password = serializers.CharField(
        label="Password",
        style={"input_type": "password"},
        write_only=True
    )
    token = serializers.CharField(label="Token", read_only=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        if phone_number and password:
            try:
                user = User.objects.get(phone_number=phone_number) 
            except User.DoesNotExist:
                raise serializers.ValidationError({"phone_number": "User does not exist."})
            
            if not user.check_password(password):
                raise serializers.ValidationError({"password": "Incorrect password."})

            if not user.is_active:
                raise serializers.ValidationError({"user": "User account is disabled."})

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Must include 'phone_number' and 'password'.")
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["phone_number", "id", "role"]  # Base fields for all users

    def to_representation(self, instance):
        # Get the default serialized data
        data = super().to_representation(instance)
        if instance.role == 'plmn_admin':
            data['plmn'] = instance.plmn  
        
        return data

    def validate(self, attrs):
        return super().validate(attrs)
    
# from rest_framework import serializers
# from django.contrib.auth import get_user_model


# User = get_user_model()

# from django.contrib.auth.password_validation import validate_password
# from django.contrib.auth import password_validation
# from django.core import exceptions as exception
# from rest_framework import serializers


# class SignUpSerializer(serializers.ModelSerializer):

#     password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
#     password1 = serializers.CharField(
#         style={'input_type': 'password'},
#         validators=[password_validation.validate_password],
#         write_only=True
#     )
#     class Meta:
#         model = User
#         fields = ('username','password1', 'password2','phone_number' )                  
#         extra_kwargs = {
#             'password1': {'write_only': True},
#             'password2': {'write_only': True},
#         }
    
#     def validate_username(self, value):
#         user = User.objects.filter(username__iexact=value)
#         if user.exists():
#             user = user.first()
#             if user.is_username_verified:
#                 raise serializers.ValidationError("username already exists.")
#             if user.phone_number != self.initial_data.get('phone_number'):
#                 raise serializers.ValidationError("username already exists.")
            
#         return str.lower(value)
    
#     def validate_password2(self, value):
        
#         if value != self.initial_data.get('password1'):
#             raise serializers.ValidationError('Passwords must match.')
#         return value
    
#     def validate_password1(self, value):
#         if value != self.initial_data.get('password2'):
#             raise serializers.ValidationError('Passwords must match.')
#         password_validation.validate_password(value)
#         return value


# class LoginSerializer(serializers.Serializer):
#     email=serializers.EmailField(
#         label=("Email"),
#     )
#     password = serializers.CharField(
#         label=("password"),
#         style={"input_type": "password"},
#         write_only=True
#     )

#     token = serializers.CharField(
#         label =("Token"),
#         read_only=True
#     )

#     def validate(self, attrs):
#         User = get_user_model()
#         email = attrs.get('email', None)
#         password = attrs.get('password', None)
#         if email and password:
#             email = self.validate_email(email)
#             user = User.objects.get(email__iexact=email)
#             if not user.check_password(password):
#                 msg = 'Incorrect password.'
#                 raise serializers.ValidationError( { "message" : msg} , code='authorization')
#             if not user.is_email_verified:
#                 raise serializers.ValidationError({"message": "User is not verified."})
#             attrs['user'] = user
#         else:
#             msg = ('Must include "email" and "password".')
#             raise serializers.ValidationError(msg, code='authorization')
#         return attrs
        
#     def validate_email(self, value):
#         msg = 'Email does not exist.'
#         user_exists = User.objects.filter(email__iexact=value).exists()

#         if not user_exists:
#             raise serializers.ValidationError( { "message" : msg} )
#         return str.lower(value)
    

# # class ActivationConfirmSerializer(serializers.Serializer):
# #     verification_code = serializers.CharField(max_length=4, min_length=4)


# # class ActivationResendSerializer(serializers.Serializer):
# #     email = serializers.EmailField(required=True)

# #     def validate(self, attrs):
# #         email = attrs.get('email', None)
# #         try:
# #             user = User.objects.get(email__iexact=email)
# #         except User.DoesNotExist:
# #             raise serializers.ValidationError({"message": "user does not exist."})

# #         if user.is_email_verified:
# #             raise serializers.ValidationError({"message": "user with this email is already verified."})

# #         attrs['user'] = user
# #         return attrs


# # class ForgotPasswordSerializer(serializers.Serializer):
# #     email = serializers.EmailField()

# # class ChangePasswordSerializer(serializers.Serializer):
# #     old_password = serializers.CharField(required=True, write_only=True)
# #     new_password = serializers.CharField(required=True, write_only=True)
# #     new_password1 = serializers.CharField(required=True, write_only=True)

# #     def validate(self, attrs):
# #         if attrs['new_password'] != attrs['new_password1']:
# #             raise serializers.ValidationError({
# #                 'new_password1': ['Passwords must match.'],
# #             })
# #         try:
# #             validate_password(attrs['new_password'])
# #         except exception.ValidationError as e:
# #             raise serializers.ValidationError({
# #                 'new_password': list(e.messages)
# #             })
# #         return attrs

# # class ResetPasswordSerializer(serializers.Serializer):
# #     new_password = serializers.CharField(write_only=True, required=True)
# #     confirm_password = serializers.CharField(write_only=True, required=True)
# #     verification_code = serializers.CharField(max_length=4, min_length=4)

# #     def validate(self, attrs):
# #         new_password = attrs.get('new_password')
# #         confirm_password = attrs.get('confirm_password')
# #         if new_password != confirm_password:
# #             raise serializers.ValidationError("New password and confirm password do not match.")
# #         try:
# #             validate_password(new_password)
# #         except serializers.ValidationError as validation_error:
# #             raise serializers.ValidationError({"new_password": validation_error})
# #         return attrs

    