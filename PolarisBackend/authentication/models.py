from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
import logging

logger = logging.getLogger(__name__)

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None):
        """
        Creates and saves a User with the given phone number and password.
        """
        if not phone_number:
            raise ValueError('User must have a phone number')
        
        user = self.model(phone_number=phone_number)
        
        # Ensure password is hashed
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None):
        """
        Creates and saves a superuser with the given phone number and password.
        """
        user = self.create_user(
            phone_number=phone_number,
            password=password
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.role = User.TYPE_ADMIN 
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, phone_number):
        """
        Retrieves a user based on the natural key, which is phone_number.
        """
        return self.get(phone_number=phone_number)

    def get_queryset(self):
        """
        Returns the queryset of users.
        """
        return super().get_queryset()


class User(AbstractBaseUser):
    TYPE_USER = "user"
    TYPE_ADMIN = "admin"
    TYPE_PLMN = "plmn_admin"
    CHOICES = (
        (TYPE_USER , "User") , 
        (TYPE_PLMN, "plmn_admin"),
        (TYPE_ADMIN , "Admin"),
    )
    
    objects = UserManager()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    phone_number_regex = r'^(?:\+98|0)(?:\s?)9[0-9]{9}$'
    phone_number_validator = RegexValidator(
        regex=phone_number_regex,
        message="Phone number must be in a valid Iranian format."
    )
    USERNAME_FIELD = 'phone_number'

    phone_number = models.CharField(
        max_length=13, 
        validators=[phone_number_validator],
        unique=True,
    )
    
    role = models.CharField( max_length=255, choices=CHOICES , default=TYPE_USER )
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False)  
    
    def get_role(self ) : 
        return self.role
    
    def __str__(self):
        return self.phone_number

    def has_perm(self , perm , obj=None ):
        "Does the user have a specific permisision?"
        return True
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True
