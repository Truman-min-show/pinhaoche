# pinche_project/exceptions.py
from rest_framework.views import exception_handler
from .utils import ApiResponse

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        return ApiResponse(data={}, code=response.status_code, message=response.data.get('detail', 'Error'))
    return response