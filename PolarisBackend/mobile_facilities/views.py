from rest_framework import views, status
from rest_framework.response import Response
from .models import UserLocationData
from authentication.models import User
from .serializers import UserLocationDataSerializer, UserLocationDataGetSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class UserLocationDataCreateView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLocationDataSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = request.user  
            serializer.save(user=user) 
            return Response({'status': 'Data Created'}, status=201)
        return Response(serializer.errors, status=400)
    
    def get(self, request):
        user = request.user
        try:
            latest_location_data = UserLocationData.objects.filter(user=user).order_by('-timestamp').first()
            if latest_location_data:
                serializer = UserLocationDataGetSerializer(latest_location_data)
                return Response(serializer.data, status=200)
            else:
                return Response({"message": "No location data found for this user."}, status=404)
        except UserLocationData.DoesNotExist:
            return Response({"message": "User location data does not exist."}, status=404)
    

class UserLocationDataListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        min_power = request.query_params.get('pmin')
        max_power = request.query_params.get('pmax')

        min_quality = request.query_params.get('qmin')
        max_quality = request.query_params.get('qmax')

        queryset = UserLocationData.objects.filter(user=request.user)

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

