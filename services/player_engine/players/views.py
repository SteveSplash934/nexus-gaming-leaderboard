import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from .models import Player

@csrf_exempt
@require_http_methods(["POST"])
def register_player(request):
    try:
        data = json.loads(request.body)
        username = data.get("username", "").strip()

        # Gateway validates too, but Player Engine ensures DB constraints
        if not username or len(username) < 3 or len(username) > 15:
            return JsonResponse(
                {
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Username must be between 3 and 15 characters",
                    },
                },
                status=422,
            )

        player = Player.objects.create(username=username)

        return JsonResponse(
            {
                "success": True,
                "message": "Player registered successfully",
                "data": {"id": str(player.id), "username": player.username},
            },
            status=201,
        )

    except IntegrityError:
        return JsonResponse(
            {
                "success": False,
                "error": {"code": "CONFLICT", "message": "Username already exists"},
            },
            status=409,
        )
    except Exception:
        return JsonResponse(
            {
                "success": False,
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "An unexpected error occurred",
                },
            },
            status=500,
        )


@require_http_methods(["GET"])
def get_internal_player(request, player_id):
    """Internal endpoint: Used by Leaderboard Engine for 'Soft Joins'"""
    try:
        player = Player.objects.get(id=player_id)
        return JsonResponse(
            {
                "success": True,
                "data": {"id": str(player.id), "username": player.username},
            },
            status=200,
        )
    except Player.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "error": {
                    "code": "PLAYER_NOT_FOUND",
                    "message": "The requested player profile does not exist",
                },
            },
            status=404,
        )


@require_http_methods(["GET"])
def health_check(request):
    """Enables the API Gateway to monitor the service health state"""
    return JsonResponse(
        {"success": True, "service": "player_engine", "status": "healthy"}, status=200
    )
