from datetime import timedelta

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *
from pinhaoche_backend.utils import ApiResponse,get_location_coordinates,calculate_distance

from pinhaoche_backend.views import ApiView

from pinhaoche_backend.settings import AMAP_API_KEY


class UserViewSet(viewsets.ModelViewSet, ApiView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return ApiResponse(data=serializer.data, code=0, message='Success')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse(data=serializer.data, code=0, message='Success')

    # 重写其他方法（retrieve, update, destroy）以使用ApiResponse

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        if 'user_type' not in request.data:
            request.data['user_type'] = 'passenger'
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return ApiResponse(
                data={'token': str(refresh.access_token)},
                code=0,
                message='注册成功'
            )
        return ApiResponse(
            data=serializer.errors,
            code=1,
            message='注册失败',
            status=status.HTTP_400_BAD_REQUEST
        )

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        try:
            user = User.objects.get(phone=phone)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return ApiResponse(
                    data={'token': str(refresh.access_token)},
                    code=0,
                    message='登录成功'
                )
            else:
                return ApiResponse(
                    data={},
                    code=1,
                    message='密码错误',
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except User.DoesNotExist:
            return ApiResponse(
                data={},
                code=1,
                message='用户不存在',
                status=status.HTTP_404_NOT_FOUND
            )



class PassengerRequestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PassengerRequestSerializer(data=request.data)
        if serializer.is_valid():
            # 获取高德地图API密钥
            amap_api_key = AMAP_API_KEY  # 替换为你的API密钥

            # 获取出发地和目的地的经纬度
            origin_address = serializer.validated_data.get('origin')
            destination_address = serializer.validated_data.get('destination')

            origin_data = get_location_coordinates(origin_address, amap_api_key)
            destination_data = get_location_coordinates(destination_address, amap_api_key)

            if not origin_data or not destination_data:
                return ApiResponse(
                    data={},
                    code=1,
                    message='无法获取地点的经纬度',
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 创建或获取出发地和目的地
            origin, _ = Location.objects.get_or_create(
                name=origin_data['name'],
                defaults={
                    'longitude': origin_data['longitude'],
                    'latitude': origin_data['latitude'],
                    'address_detail': origin_data['address_detail']
                }
            )

            destination, _ = Location.objects.get_or_create(
                name=destination_data['name'],
                defaults={
                    'longitude': destination_data['longitude'],
                    'latitude': destination_data['latitude'],
                    'address_detail': destination_data['address_detail']
                }
            )

            # 获取当前登录用户
            passenger = request.user

            # 创建乘客请求
            passenger_request = PassengerRequest.objects.create(
                passenger=passenger,
                origin=origin,
                destination=destination,
                departure_time=serializer.validated_data.get('departure_time'),
                seats_needed=serializer.validated_data.get('seats_needed')
            )

            return ApiResponse(
                data={'ride_id': passenger_request.id},
                code=0,
                message='拼车请求创建成功'
            )
        return ApiResponse(
            data=serializer.errors,
            code=1,
            message='创建拼车请求失败',
            status=status.HTTP_400_BAD_REQUEST
        )

class AvailableRequestView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AvailableRequestSerializer(data=request.data)
        if serializer.is_valid():
            # 获取筛选条件
            origin_name = serializer.validated_data.get('origin')
            destination_name = serializer.validated_data.get('destination')
            departure_time = serializer.validated_data.get('departure_time')

            # 构建查询条件
            query = PassengerRequest.objects.all()

            # 地点匹配
            if origin_name:
                # 关键词匹配
                query = query.filter(
                    Q(origin__name__icontains=origin_name) |
                    Q(origin__address_detail__icontains=origin_name)
                )
                # 经纬度匹配（如果提供了经纬度）
                origin_lat = request.data.get('origin_lat')
                origin_lon = request.data.get('origin_lon')
                if origin_lat and origin_lon:
                    filtered_requests = []
                    for req in query:
                        distance = calculate_distance(
                            float(origin_lat),
                            float(origin_lon),
                            req.origin.latitude,
                            req.origin.longitude
                        )
                        if distance <= 10:  # 距离在10公里以内
                            filtered_requests.append(req)
                    query = filtered_requests

            if destination_name:
                # 关键词匹配
                query = query.filter(
                    Q(destination__name__icontains=destination_name) |
                    Q(destination__address_detail__icontains=destination_name)
                )
                # 经纬度匹配（如果提供了经纬度）
                destination_lat = request.data.get('destination_lat')
                destination_lon = request.data.get('destination_lon')
                if destination_lat and destination_lon:
                    filtered_requests = []
                    for req in query:
                        distance = calculate_distance(
                            float(destination_lat),
                            float(destination_lon),
                            req.destination.latitude,
                            req.destination.longitude
                        )
                        if distance <= 1:  # 距离在1公里以内
                            filtered_requests.append(req)
                    query = filtered_requests

            # 时间匹配
            if departure_time:
                query = query.filter(
                    departure_time__gte=departure_time - timedelta(minutes=5),
                    departure_time__lte=departure_time + timedelta(minutes=5)
                )

            # 构造返回的数据格式
            result = []
            for req in query:
                result.append({
                    'ride_id': req.id,
                    'origin': req.origin.address_detail,
                    'destination': req.destination.address_detail,
                    'departure_time': req.departure_time.isoformat(),
                    'seats_needed': req.seats_needed,
                    'passenger': {
                        'username': req.passenger.username,
                        'phone': req.passenger.phone
                    }
                })

            return ApiResponse(
                data={'requests': result},
                code=0,
                message='success'
            )
        return ApiResponse(
            data=serializer.errors,
            code=1,
            message='筛选条件无效',
            status=status.HTTP_400_BAD_REQUEST
        )