from rest_framework import views, status
from rest_framework.response import Response
from .models import UserMobileTests
from authentication.models import User
from .serializers import UserMobileTestSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

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
            distinct_domains = queryset.values_list('test_domain', flat=True).distinct()
            domains_string = ",".join(distinct_domains)
            return Response(domains_string, status=status.HTTP_200_OK)

        
