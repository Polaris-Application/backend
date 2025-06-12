from .views import *
from django.urls import path


urlpatterns = [
    path('signup/' , SignUpView.as_view() , name='signup' ) ,
    path('login/',LoginView.as_view(),name='Login'),
    path('logout/',LogoutView.as_view(),name='Logout'),
    path('get_user/' , RetrieveUserData.as_view() , name='get_user'),
    # path('activation_confirm/<str:token>/', ActivationConfirmView.as_view(), name='activation_confirm'),
    # path('activation_resend/', ActivationResend.as_view(), name='activation_resend'),
    # path('forgot_password/' , ForgotPassword.as_view() , name='forgot_password'),
    # path('reset_password/<str:token>/', ResetPassword.as_view(), name='reset_password'),
    # path('complete_info/' , CompleteInfoView.as_view() , name= 'complete_info') , 
    # path('change_password/' , ChangePasswordView.as_view() , name='change_password'),
]
