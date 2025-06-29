from rest_framework import views, status
from rest_framework.response import Response
from .models import UserLocationData
from authentication.models import User
from .serializers import UserLocationDataSerializer, UserLocationDataGetSerializer, SignalStrengthSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Count
from django.utils.dateparse import parse_datetime
from datetime import datetime

class UserLocationDataCreateView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLocationDataSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user  
            serializer.save(user=user) 
            return Response({'status': 'Data Created'}, status=201)
       
        return Response(serializer.errors , status=400)
    
    def get(self, request):
        user = request.user
        try:
            latest_location_data = UserLocationData.objects.order_by('-timestamp').first()
            if user.role == "plmn_admin": 
                latest_location_data = latest_location_data.filter(plmn_id=user.plmn)
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
        user = request.user
        latest_location_data = UserLocationData.objects.order_by('-timestamp')
        if user.role == "plmn_admin": 
            latest_location_data = latest_location_data.filter(plmn_id=user.plmn)
        elif user.role == "user": 
            latest_location_data = latest_location_data.filter(user=user)

        queryset = UserLocationData.objects.filter(
            rsrp__isnull=False,
            rsrq__isnull=False
        ).values('rsrp', 'rsrq')  

        return Response(list(queryset), status=200)
    

class HistogramDataView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # RSRP / RSSI / RSRQ
        rsrp = request.query_params.get("rsrp")
        rsrq = request.query_params.get("rsrq")
        rssi = request.query_params.get("rssi")
        user = request.user
        latest_location_data = UserLocationData.objects.order_by('-timestamp')
        if user.role == "plmn_admin": 
            latest_location_data = latest_location_data.filter(plmn_id=user.plmn)
        elif user.role == "user": 
            latest_location_data = latest_location_data.filter(user=user)
        if rsrp : 
            queryset = UserLocationData.objects.filter( rsrp__isnull=False).values_list('rsrp', flat=True)
            return Response(list(queryset), status=200)
        if rsrq : 
            queryset = UserLocationData.objects.filter( rsrp__isnull=False).values_list('rsrq', flat=True)
            return Response(list(queryset), status=200)
        if rssi : 
            queryset = UserLocationData.objects.filter( rsrp__isnull=False).values_list('rssi', flat=True)
            return Response(list(queryset), status=200)
        return Response({"message": "no parameter were provided!"}, status=400)
    

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
            queryset = queryset.filter(plmn_id=user.plmn)
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

    def get_grouped_rsrp_data(self, queryset, scale):
        grouped_data = {}
        for item in queryset:
            ts = item['timestamp']
            rsrp = item['rsrp']

            if scale == '1h':
                key = ts.strftime('%Y-%m-%d %H:00')
            elif scale == '1d':
                key = ts.strftime('%Y-%m-%d')
            elif scale == '1w':
                # iso_year, iso_week, _ = ts.isocalendar()
                year = ts.year
                month = ts.month
                first_day_of_month = datetime(year, month, 1)
                week_num_in_month = ((ts.day + first_day_of_month.weekday()) - 1) // 7 + 1
                key = f"{year}-{month:02d}-w{week_num_in_month}"
                # key = f"{iso_year}-w{iso_week}"
            elif scale == '1m':
                key = ts.strftime('%Y-%m')
            else:
                key = ts.isoformat()

            if key not in grouped_data:
                grouped_data[key] = {'rsrp_sum': 0, 'count': 0}

            grouped_data[key]['rsrp_sum'] += rsrp
            grouped_data[key]['count'] += 1

        result = []
        for key, value in grouped_data.items():
            avg_rsrp = value['rsrp_sum'] / value['count']
            result.append({
                'timestamp': key,
                'rsrp': avg_rsrp
            })
        result.sort(key=lambda x: x['timestamp'])
        return result

    def get(self, request):
        user = request.user
        cell_id = request.query_params.get('cell_id')
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        scale = request.query_params.get('scale')

        queryset = UserLocationData.objects.filter(rsrp__isnull=False)
        
        if user.role == "plmn_admin":
            queryset = queryset.filter(plmn_id=user.plmn)
        elif user.role == "user":
            queryset = queryset.filter(user=user)

        if cell_id:
            queryset = queryset.filter(cell_id=cell_id)
        if start:
            start_dt = parse_datetime(start)
            if start_dt:
                queryset = queryset.filter(timestamp__gte=start_dt)

        if end:
            end_dt = parse_datetime(end)
            if end_dt:
                queryset = queryset.filter(timestamp__lte=end_dt)

        queryset = queryset.order_by('timestamp').values('timestamp', 'rsrp')
        if scale : #start and end
            data = self.get_grouped_rsrp_data(queryset, scale)
        else:
            data = list(queryset)
        return Response(data, status=200)


# class RSRPOverTimeView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         cell_id = request.query_params.get('cell_id')
#         start = request.query_params.get('start')  # e.g., 2025-06-01T00:00:00
#         end = request.query_params.get('end')

#         queryset = UserLocationData.objects.filter( rsrp__isnull=False)
#         if user.role == "plmn_admin": 
#             queryset = queryset.filter(plmn_id=user.plmn)
#         elif user.role == "user": 
#             queryset = queryset.filter(user=user)
       
#         if cell_id:
#             queryset = queryset.filter(cell_id=cell_id)

#         if start:
#             queryset = queryset.filter(timestamp__gte=parse_datetime(start))
#         if end:
#             queryset = queryset.filter(timestamp__lte=parse_datetime(end))

#         queryset = queryset.order_by('timestamp').values('timestamp', 'rsrp')
#         return Response(list(queryset), status=200)

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
            queryset = queryset.filter(plmn_id=user.plmn)
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

