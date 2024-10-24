from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from survivorapi.models import Survivor, Season

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [
            'id', 'season_number', 'name', 'location',
            'start_date', 'end_date', 'is_current'
        ]

class SurvivorSerializer(serializers.ModelSerializer):
    season = SeasonSerializer(read_only=True) # For GET requests
    season_id = serializers.IntegerField(write_only=True) # For POST/PUT requests
    
    class Meta:
        model = Survivor
        fields = ['id', 'season', 'season_id', 'first_name', 'last_name', 'age', 'img_url']

class Survivors(viewsets.ModelViewSet):
    """
    A ViewSet for viewing, creating, deleting, and updating Survivor instances.
    
    Provides default implementations for:
    - list (GET)
    - retrieve (GET detail)
    - update (PUT)
    - destroy (DELETE)

    Provides custom implementations for:
    - create (POST)
    """
    queryset = Survivor.objects.all()
    serializer_class = SurvivorSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Optionally restricts the returned survivors to a given season,
        by filtering against a 'season' query param in the URL
        """
        queryset = Survivor.objects.all()
        season = self.request.query_params.get('season_number', None)

        if season is not None:
            queryset = queryset.filter(season_id=season)
        
        # Will define more query_params

        return queryset
    
    def create(self, request, *args, **kwargs):
        """Method for admin user to create a survivor instance"""

        season_id = request.data["season_id"]
        season = Season.objects.get(pk=season_id)

        try:
            survivor = Survivor.objects.create(
                season = season,
                first_name = request.data["first_name"],
                last_name = request.data["last_name"],
                age = request.data["age"],
                img_url = request.data["img_url"]
            )
        
            serializer = SurvivorSerializer(survivor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)