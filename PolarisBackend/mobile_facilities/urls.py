from django.urls import path
from .views import UserLocationDataCreateView, UserLocationDataListView

urlpatterns = [
    path('location-data/', UserLocationDataCreateView.as_view(), name='location-data'),
    path('list-location-data/',UserLocationDataListView.as_view(), name='power-location-data' ),
]
