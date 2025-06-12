from django.urls import path
from .views import UserLocationDataCreateView, PowerUserLocationDataListView, QualityUserLocationDataListView

urlpatterns = [
    path('location-data/', UserLocationDataCreateView.as_view(), name='location-data'),
    path('power-location-data/',PowerUserLocationDataListView.as_view(), name='power-location-data' ),
    path('quality-location-data/',QualityUserLocationDataListView.as_view(), name='quality-location-data' ),
]
