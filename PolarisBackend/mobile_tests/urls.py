from django.urls import path
from .views import UserMobileTestsView, MaxPingOverTimeView, EventCountApiView

urlpatterns = [
    path('user/', UserMobileTestsView.as_view(), name='tests'),
    path('max-over-time/', MaxPingOverTimeView.as_view(), name='max-ping-over-time'),
    path('event-count/', EventCountApiView.as_view(), name='event-count'),
]