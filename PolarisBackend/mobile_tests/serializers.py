from rest_framework import serializers
from .models import UserMobileTests


class UserMobileTestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = UserMobileTests
        fields = '__all__'
