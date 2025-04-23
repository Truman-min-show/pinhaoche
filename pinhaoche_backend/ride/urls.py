from django.urls import path
from .views import *

urlpatterns = [
    path('users/register', RegisterView.as_view(), name='register'),
    path('users/login', LoginView.as_view(), name='login'),
    path('rides', PassengerRequestView.as_view(), name='passenger-request'),
    path('rides/search', AvailableRequestView.as_view(), name='available-requests'),
]