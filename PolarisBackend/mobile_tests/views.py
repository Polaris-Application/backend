from rest_framework import views, status
from rest_framework.response import Response
from .models import UserMobileTests
from authentication.models import User
from .serializers import UserMobileTestSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models.functions import TruncMinute, TruncDay, TruncHour, TruncMonth, TruncWeek
from django.db.models import Max
from mobile_facilities.models import UserLocationData
from authentication.models import User
from django.utils.dateparse import parse_datetime
from datetime import timedelta
from django.db.models import Avg
from django.db.models import Count
from datetime import datetime


class UserMobileTestsView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserMobileTestSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user  
            serializer.save(user=user) 
            return Response({'status': 'Data Created'}, status=201)
        return Response(serializer.errors, status=400)
    
    def get_grouped_result_data(self, queryset, scale, start, end, name, domain):
        if start:
            start_dt = parse_datetime(start)
            if start_dt:
                queryset = queryset.filter(timestamp__gte=start_dt)
        if end:
            end_dt = parse_datetime(end)
            if end_dt:
                queryset = queryset.filter(timestamp__lte=end_dt)

        grouped_data = {}
        for item in queryset:
            ts = item.timestamp
            result = item.result

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
                grouped_data[key] = {'result_sum': 0, 'count': 0}

            grouped_data[key]['result_sum'] += result
            grouped_data[key]['count'] += 1

        result = []
        for key, value in grouped_data.items():
            avg_result = value['result_sum'] / value['count']
            result.append({
                'timestamp': key,
                'result': avg_result,
                'name': name , 
                'test_domain': domain
            })
        return result

    def get(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        scale = request.query_params.get('scale')

        domain = request.query_params.get('domain')
        name = request.query_params.get('name')
        queryset = UserMobileTests.objects.filter(user=request.user)
        if (not name) and ( not domain): 
            queryset = queryset.order_by('timestamp')
            serializer = UserMobileTestSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if domain and name :
            queryset = queryset.filter(name__icontains=name)
            queryset = queryset.filter(test_domain__icontains=domain).order_by('timestamp')
            if scale:
                result = self.get_grouped_result_data(queryset=queryset, start=start,end=end, scale=scale, name=name, domain=domain)
                return Response(result, status=status.HTTP_200_OK)
            serializer = UserMobileTestSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if name in ["down","up"]: 
                queryset = queryset.filter(name__icontains=name).order_by('timestamp')
                if scale:
                    result = self.get_grouped_result_data(queryset=queryset, start=start,end=end, scale=scale, name=name, domain='')
                    return Response(result, status=status.HTTP_200_OK)
                serializer = UserMobileTestSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            queryset = queryset.filter(name__icontains=name)
            distinct_domains = queryset.values_list('test_domain', flat=True).distinct()
            domains_string = ",".join(distinct_domains)
            return Response(domains_string, status=status.HTTP_200_OK)
        

class EventCountApiView(APIView): 
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            cell_info_queryset = UserLocationData.objects.order_by('-timestamp')
            if user.role == "admin" : 
                user_count = User.objects.count()
                cell_info_count = UserLocationData.objects.count()
                return Response( {"user_count": user_count, 
                                  "cell_info_count": cell_info_count}, status=200)
            elif user.role == "plmn_admin": 
                temp = cell_info_queryset.filter(plmn_id=user.plmn)
                cell_info_count = temp.count()
                user_count = temp.values_list("user", flat=True).distinct().count()
                return Response( {"user_count": user_count, 
                                  "cell_info_count": cell_info_count}, status=200)
            elif user.role == "user": 
                cell_info_count = cell_info_queryset.filter(user=user).count()
                user_test_count = UserMobileTests.objects.filter(user=user).count()
                return Response( {"user_test_count": user_test_count, 
                                  "cell_info_count": cell_info_count}, status=200)
        except UserLocationData.DoesNotExist:
            return Response({"message": "User location data does not exist."}, status=404)  



class MaxPingOverTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        scale = request.query_params.get('scale', '1m').lower()

        queryset = UserMobileTests.objects.filter(user=request.user, name='ping')

        if start:
            start_dt = parse_datetime(start)
            if start_dt:
                queryset = queryset.filter(timestamp__gte=start_dt)
        if end:
            end_dt = parse_datetime(end)
            if end_dt:
                queryset = queryset.filter(timestamp__lte=end_dt)

        # Determine truncation function based on scale
        trunc_func = self.get_trunc_function(scale)

        if trunc_func is None:
            trunc_func = TruncMinute(15)
            # return Response({"error": "Invalid scale. Use one of: 1m, 1h, 1d, 1w, 1mo"},
            #                 status=status.HTTP_400_BAD_REQUEST)

        queryset = (
            queryset
            .annotate(time_bin=trunc_func)
            .values('time_bin')
            .annotate(max_delay=Max('result'))
            .order_by('time_bin')
        )

        data = [{"timestamp": item["time_bin"], "max_delay": item["max_delay"]} for item in queryset]
        return Response(data, status=status.HTTP_200_OK)

    def get_trunc_function(self, scale):
        if scale == '1m':
            return TruncMinute('timestamp')
        elif scale == '1h':
            return TruncHour('timestamp')
        elif scale == '1d':
            return TruncDay('timestamp')
        elif scale == '1w':
            return TruncWeek('timestamp')
        elif scale == '1mo':
            return TruncMonth('timestamp')
        else:
            return None


# class MaxPingOverTimeView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         start = request.query_params.get('start')
#         end = request.query_params.get('end')
#         interval = int(request.query_params.get('scale', 30))
#         queryset = UserMobileTests.objects

#         if start:
#             start_dt = parse_datetime(start)
#             if start_dt:
#                 queryset = queryset.filter(timestamp__gte=start_dt)
#         if end:
#             end_dt = parse_datetime(end)
#             if end_dt:
#                 queryset = queryset.filter(timestamp__lte=end_dt)

#         user = request.user
#         # Truncate to 5-minute bins
#         trunc_func = TruncMinute('timestamp', precision=interval)

#         queryset = (
#             queryset
#             .filter(user=user, name='ping')
#             .annotate(time_bin=trunc_func)
#             .values('time_bin')
#             .annotate(max_delay=Max('result'))
#             .order_by('time_bin')
#         )
#         data = [{"timestamp": item["time_bin"], "max_delay": item["max_delay"]} for item in queryset]
#         return Response(data,status=status.HTTP_200_OK)
    

