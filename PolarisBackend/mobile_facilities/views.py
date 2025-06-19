from rest_framework import views, status
from rest_framework.response import Response
from .models import UserLocationData
from authentication.models import User
from .serializers import UserLocationDataSerializer, UserLocationDataGetSerializer, SignalStrengthSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Count
from django.utils.dateparse import parse_datetime


class UserLocationDataCreateView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLocationDataSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user  
            serializer.save(user=user) 
            return Response({'status': 'Data Created'}, status=201)
        print(f"++++++++++++++++++++++++++++++++++++++++ {serializer.errors}" )
        return Response(serializer.errors , status=400)
    
    def get(self, request):
        user = request.user
        try:
            latest_location_data = UserLocationData.objects.order_by('-timestamp').first()
            if user.role == "plmn_admin": 
                latest_location_data = latest_location_data.filter(plmn=user.plmn)
            elif user.role == "user": 
                latest_location_data = latest_location_data.filter(user=user)

            if latest_location_data:
                serializer = UserLocationDataGetSerializer(latest_location_data)
                return Response(serializer.data, status=200)
            else:
                return Response({"message": "No location data found for this user."}, status=404)
        except UserLocationData.DoesNotExist:
            return Response({"message": "User location data does not exist."}, status=404)  


class SignalScatterDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = UserLocationData.objects.filter(
            user=request.user,
            rsrp__isnull=False,
            rsrq__isnull=False
        ).values('rsrp', 'rsrq')  

        return Response(list(queryset), status=200)
    
class UserLocationDataListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        min_power = request.query_params.get('pmin')
        max_power = request.query_params.get('pmax')

        min_quality = request.query_params.get('qmin')
        max_quality = request.query_params.get('qmax')

        queryset = UserLocationData.objects
        if request.user.role == "plmn_admin": 
            queryset = queryset.filter(plmn=request.user.plmn)
        elif request.user.role == "user": 
            queryset = queryset.filter(user=request.user)

        if min_power:
            queryset = queryset.filter(power__gte=min_power)
        if max_power:
            queryset = queryset.filter(power__lte=max_power)
        queryset = UserLocationData.objects.filter(user=request.user)
        if min_quality:
            queryset = queryset.filter(quality__gte=min_quality)
        if max_quality:
            queryset = queryset.filter(quality__lte=max_quality)
        serializer = UserLocationDataGetSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NetworkTypeUsagePieView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        queryset = UserLocationData.objects
        if user.role == "plmn_admin": 
            queryset = queryset.filter(plmn=user.plmn)
        elif user.role == "user": 
            queryset = queryset.filter(user=user)

        if start:
            queryset = queryset.filter(timestamp__gte=parse_datetime(start))
        if end:
            queryset = queryset.filter(timestamp__lte=parse_datetime(end))

        result = (
            queryset
            .values('network_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return Response(list(result))


class RSRPOverTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cell_id = request.query_params.get('cell_id')
        start = request.query_params.get('start')  # e.g., 2025-06-01T00:00:00
        end = request.query_params.get('end')

        queryset = UserLocationData.objects.filter( rsrp__isnull=False)
        if user.role == "plmn_admin": 
            queryset = queryset.filter(plmn=user.plmn)
        elif user.role == "user": 
            queryset = queryset.filter(user=user)
       
        if cell_id:
            queryset = queryset.filter(cell_id=cell_id)

        if start:
            queryset = queryset.filter(timestamp__gte=parse_datetime(start))
        if end:
            queryset = queryset.filter(timestamp__lte=parse_datetime(end))

        queryset = queryset.order_by('timestamp').values('timestamp', 'rsrp')
        return Response(list(queryset), status=200)

class ARFCNUsagePieView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        network_type_param = request.query_params.get('network_type')

        if not network_type_param:
            return Response(
                {"error": "Missing required parameter: network_type"},
                status=400
            )
        queryset = UserLocationData.objects
        if user.role == "plmn_admin": 
            queryset = queryset.filter(plmn=user.plmn)
        elif user.role == "user": 
            queryset = queryset.filter(user=user)
            
        queryset = (
            queryset
            .filter(
                network_type__icontains=network_type_param,
                arfcn__isnull=False
            )
            .values('arfcn')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        result = [
            {
                "arfcn": item["arfcn"],
                "network_type": network_type_param,
                "count": item["count"]
            }
            for item in queryset
        ]

        return Response(result, status=200)

