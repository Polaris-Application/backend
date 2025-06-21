from rest_framework import views, status
from rest_framework.response import Response
from .models import UserMobileTests
from authentication.models import User
from .serializers import UserMobileTestSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models.functions import TruncMinute
from django.db.models import Max
from mobile_facilities.models import UserLocationData
from authentication.models import User

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
    
    def get(self, request):
        domain = request.query_params.get('domain')
        name = request.query_params.get('name')
        queryset = UserMobileTests.objects.filter(user=request.user)
        if (not name) and ( not domain): 
            queryset = queryset.order_by('timestamp')
            serializer = UserMobileTestSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        queryset = queryset.filter(name__icontains=name)
        if domain: 
            queryset = queryset.filter(test_domain__icontains=domain).order_by('timestamp')
            serializer = UserMobileTestSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if name == "down" or "up": 
                queryset = queryset.filter(name__icontains=name).order_by('timestamp')
                serializer = UserMobileTestSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
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
        interval_minutes = int(request.query_params.get('interval', 5))
        user = request.user

        # Truncate to 5-minute bins
        trunc_func = TruncMinute('timestamp', precision=interval_minutes)

        queryset = (
            UserMobileTests.objects
            .filter(user=user, name='ping')
            .annotate(time_bin=trunc_func)
            .values('time_bin')
            .annotate(max_delay=Max('result'))
            .order_by('time_bin')
        )
        data = [{"timestamp": item["time_bin"], "max_delay": item["max_delay"]} for item in queryset]
        return Response(data,status=status.HTTP_200_OK)
    

