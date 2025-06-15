from django.urls import path
from .views import UserMobileTestsView

urlpatterns = [
    path('user/', UserMobileTestsView.as_view(), name='tests'),
]