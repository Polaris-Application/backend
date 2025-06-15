from rest_framework import serializers
from .models import UserLocationData


class UserLocationDataSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = UserLocationData
        fields = '__all__'


class SignalStrengthSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocationData
        fields = ['rsrp', 'rsrq']

class UserLocationDataGetSerializer(serializers.ModelSerializer):
    tac_lac = serializers.SerializerMethodField()
    # Power = serializers.SerializerMethodField()
    # Power_description = serializers.SerializerMethodField()
    # Quality = serializers.SerializerMethodField()
    # Quality_description = serializers.SerializerMethodField()

    class Meta:
        model = UserLocationData
        fields = [
            "user",
            "timestamp",
            "latitude",
            "longitude",
            "plmn_id",
            "tac_lac",
            "cell_id",
            "band",
            "arfcn",
            "network_type",
            "power",
            "rsrp",
            "rsrq",
            "rssi" ,
            "rscp",
            # "Power_description",
            "quality",
            # "Quality_description",
        ]

    # def get_Power(self, obj):
    #     return obj.get_signal_power()["Power"]

    # def get_Power_description(self, obj):
    #     return obj.get_signal_power()["Power_description"]

    # def get_Quality(self, obj):
    #     return obj.get_signal_quality()["Quality"]

    # def get_Quality_description(self, obj):
    #     return obj.get_signal_quality()["Quality_description"]

    def get_tac_lac(self, obj):
        return obj.get_tac_lac()
