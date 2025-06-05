from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self , username , phone_number ,password=None) :   #phone = None , firstname , lastname 
        """
        Creates and saves a User with the given username, 
        data of birth and password
        """
        if not username: 
            raise ValueError('User must have username')
        
        user = self.model(
            username = username,
            phone_number = phone_number 
        )
        user.password = make_password(password)
        user.save(using=self._db)
        return user
    
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset()
    
    def create_superuser(self , username ,password=None):
        """
        Creates and saves a superuser with the given username, birthdat
        and password.
        """
        user = self.create_user(
            username=username,
            password=password,
            phone_number="09999999999" 
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.role = User.TYPE_ADMIN
        user.save(using=self._db)
        return user

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)

    def get_by_natural_key(self, username):
        return self.get(username=username)

class User(AbstractBaseUser):
    TYPE_USER = "user"
    TYPE_ADMIN = "admin"
    TYPE_PLMN = "plmn_admin"

    CHOICES = (
        (TYPE_USER , "User") , 
        (TYPE_PLMN, "plmn_admin"),
        (TYPE_ADMIN , "Admin"),
    )
    
    username = models.CharField(
        max_length=255,
        unique=True,
        blank=False,
        null=False
    )
    USERNAME_FIELD = 'username'

    
    objects = UserManager()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    phone_number_regex = r'^(?:\+98|0)(?:\s?)9[0-9]{9}$'
    phone_number_validator = RegexValidator(
        regex=phone_number_regex,
        message="Phone number must be in a valid Iranian format."
    )

    phone_number = models.CharField(
        max_length=11, 
        validators=[phone_number_validator],
        blank=True,
        null=True
    )
    
    role = models.CharField( max_length=255, choices=CHOICES , default=TYPE_USER )
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False)  
    
    def get_role(self ) : 
        return self.role
    
    def __str__(self):
        return self.username

    def has_perm(self , perm , obj=None ):
        "Does the user have a specific permisision?"
        return True
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True
