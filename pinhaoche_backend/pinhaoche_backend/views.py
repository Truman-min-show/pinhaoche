# pinche_project/views.py
from rest_framework.views import APIView
from .utils import ApiResponse

class ApiView(APIView):
    def get(self, request, *args, **kwargs):
        return ApiResponse(data={}, code=0, message='Success')

    def post(self, request, *args, **kwargs):
        return ApiResponse(data={}, code=0, message='Success')

    def put(self, request, *args, **kwargs):
        return ApiResponse(data={}, code=0, message='Success')

    def delete(self, request, *args, **kwargs):
        return ApiResponse(data={}, code=0, message='Success')