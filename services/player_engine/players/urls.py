from django.urls import path
from . import views

urlpatterns = [
    path('api/v1/players/register', views.register_player, name='register_player'),
    
    path('internal/players/<uuid:player_id>', views.get_internal_player, name='internal_player'),
    path('health', views.health_check, name='health_check'),
]