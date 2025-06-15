from django.urls import path
from .views import UserLocationDataCreateView, UserLocationDataListView \
                    ,SignalScatterDataView, NetworkTypeUsagePieView, RSRPOverTimeView \
                    ,ARFCNUsagePieView                  

urlpatterns = [
    path('location-data/', UserLocationDataCreateView.as_view(), name='location-data'),
    path('list-location-data/',UserLocationDataListView.as_view(), name='location_data' ),
    path('scatter-data/', SignalScatterDataView.as_view(), name='scatter-data'),
    path('network-type-usage/', NetworkTypeUsagePieView.as_view(), name='network-type-usage'),
    path('rsrp-over-time/', RSRPOverTimeView.as_view(), name='rsrp-over-time'),
    path('arfcn-usage/', ARFCNUsagePieView.as_view(), name='arfcn-usage'),
]
