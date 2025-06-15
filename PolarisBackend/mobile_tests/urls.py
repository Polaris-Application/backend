from django.urls import path
from .views import UserMobileTestsView, MaxPingOverTimeView

urlpatterns = [
    path('user/', UserMobileTestsView.as_view(), name='tests'),
    path('max-over-time/', MaxPingOverTimeView.as_view(), name='max-ping-over-time'),
]