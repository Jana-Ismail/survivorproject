from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from survivorapi.models import Tribe, Season

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [
            'id', 'season_number', 'name', 'location',
            'start_date', 'end_date', 'is_current'
        ]

class TribeSerializer(serializers.ModelSerializer):
    season = SeasonSerializer(read_only=True) # For GET requests
    season_id = serializers.IntegerField(write_only=True) # For POST/PUT requests

    class Meta:
        model = Tribe
        fields = ['id', 'season', 'season_id', 'name', 'color', 'is_merge_tribe']

class Tribes(viewsets.ModelViewSet):
    """
    A ViewSet for viewing, creating, deleting, and updating Tribe instances.
    """
    queryset = Tribe.objects.all()
    serializer_class = TribeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def create(self, request):
        """Method for admin user to create a tribe instance"""
        
        season_id = request.data["season_id"]
        season = Season.objects.get(pk=season_id)
        
        try:
            tribe = Tribe.objects.create(
                season = season,
                name = request.data["name"],
                color = request.data["color"],
                is_merge_tribe = request.data["is_merge_tribe"]
            )

            serializer = TribeSerializer(tribe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)