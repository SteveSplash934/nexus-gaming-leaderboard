from django.urls import path
from . import views

urlpatterns = [
    # Exposed to external via API Gateway
    path('api/v1/players/register', views.register_player, name='register_player'),
    
    # Internal route, hidden from the public
    path('internal/players/<uuid:player_id>', views.get_internal_player, name='internal_player'),
]