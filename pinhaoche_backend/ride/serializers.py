from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate_phone(self, value):
        # 检查 phone 是否唯一
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已注册")
        return value

    def validate_password(self, value):
        # 检查 password 是否满足最小长度
        if len(value) < 8:
            raise serializers.ValidationError("密码长度至少为8位")
        return value

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            phone=validated_data['phone'],
            user_type=validated_data.get('user_type', 'passenger')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class CarpoolOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarpoolOrder
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class PassengerRequestSerializer(serializers.ModelSerializer):
    origin = serializers.CharField()
    destination = serializers.CharField()

    class Meta:
        model = PassengerRequest
        fields = ['origin', 'destination', 'departure_time', 'seats_needed']

    def validate_seats_needed(self, value):
        if value <= 0:
            raise serializers.ValidationError("所需座位数必须大于0")
        return value

class AvailableRequestSerializer(serializers.Serializer):
    origin = serializers.CharField(required=False)
    destination = serializers.CharField(required=False)
    departure_time = serializers.DateTimeField(required=False)
    origin_lat = serializers.DecimalField(required=False, max_digits=9, decimal_places=6)
    origin_lon = serializers.DecimalField(required=False, max_digits=9, decimal_places=6)
    destination_lat = serializers.DecimalField(required=False, max_digits=9, decimal_places=6)
    destination_lon = serializers.DecimalField(required=False, max_digits=9, decimal_places=6)