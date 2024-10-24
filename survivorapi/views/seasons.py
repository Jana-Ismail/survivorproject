# from django.http import HttpResponseServerError
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
# from rest_framework.decorators import action
from survivorapi.models import Season

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [
            'id', 'season_number', 'name', 'location',
            'start_date', 'end_date', 'is_current'
        ]

class Seasons(viewsets.ModelViewSet):
    """
    A ViewSet for viewing, creating, deleting, and updating Season instances.

    Provides default implementations for:
    - list (GET)
    - retrieve (GET detail)
    - update (PUT)
    - destroy (DELETE)

    Provides custom implementations for:
    - create (POST)

    admin user data:
        user info:
            id: 3
            token: ec7ddcc665035a3adeaa80ed8f812bfe3ef5b5f4

    """
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Method for admin user to create a season instance"""
        try:
            season = Season.objects.create(
                season_number=request.data["season_number"],
                name=request.data["name"],
                location=request.data["location"],
                start_date=request.data["start_date"],
                end_date=request.data["end_date"],
                is_current=request.data["is_current"]
            )

            serializer = SeasonSerializer(season)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)