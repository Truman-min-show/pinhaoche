# pinhaoche_backend/utils.py
import requests
from rest_framework.response import Response
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine公式计算两点之间的距离（公里）
    R = 6371  # 地球半径（公里）
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
class ApiResponse(Response):
    def __init__(self, data=None, code=0, message='Success', status=None, template_name=None, headers=None, exception=False, content_type=None):
        super().__init__(
            data={'code': code, 'message': message, 'data': data},
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type
        )

def custom_exception_handler(exc, context):
    from rest_framework.views import exception_handler
    response = exception_handler(exc, context)
    if response is not None:
        return ApiResponse(
            data={},
            code=response.status_code,
            message=response.data.get('detail', 'Error'),
            status=response.status_code
        )
    return response


def get_location_coordinates(address, api_key):
    url = f"https://restapi.amap.com/v3/geocode/geo"
    params = {
        "key": api_key,
        "address": address,
        "output": "JSON",
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get('status') == '1' and data.get('geocodes'):
        geocode = data['geocodes'][0]
        return {
            "name": address,
            "longitude": geocode['location'].split(',')[0],
            "latitude": geocode['location'].split(',')[1],
            "address_detail": geocode.get('formatted_address', '')
        }
    else:
        print(f"高德地图API响应: {data}")  # 调试信息
    return None