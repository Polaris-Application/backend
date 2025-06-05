from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms
from .models import User 
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'phone_number' , 'role')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username', 'password', 'is_active', 'is_admin', 'phone_number', 'role')

    def clean_password(self):
        return self.initial["password"]

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'is_admin', 'is_active', 'phone_number', 'role')
    list_filter = ('is_admin', 'role')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('phone_number', 'role')}),
        ('Permissions', {'fields': ('is_admin', 'is_active')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone_number', 'role', 'password1', 'password2', 'is_active'),
        }),
    )

    search_fields = ('username', 'phone_number')
    ordering = ('username',)
    filter_horizontal = ()

    

# class UserAdmin(BaseUserAdmin):
#     form = UserChangeForm
#     add_form= UserCreationForm
#     list_display = ('email' ,'username', 'is_admin' , 'is_active' , 'phone_number' , 'role')   #'is_email_verified'   'phone_number'
#     list_filter = ('is_admin' , 'email' ,'tname' , 'phone_number' , 'role')
#     fieldsets=(
#         (None, {'fields': ('email', 'password')}),
#         ('Personal info', {'fields': ('username' ,'phone_number' , 'role')}), ## 'phone_number'
#         ('Permissions', {'fields': ( 'is_admin', 'is_active','is_email_verified' )}),   #'is_email_verified'
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2', 'is_active'  ),   # , 'date_of_birth'
#         }),
#     )

#     search_fields = ('email',)
#     ordering = ('email',)
#     filter_horizontal = ()

admin.site.register(User, UserAdmin )
