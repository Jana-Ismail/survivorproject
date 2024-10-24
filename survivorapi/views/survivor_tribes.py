from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from survivorapi.models import SurvivorTribe, Survivor, Tribe, Season

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
        fields = ['id', 'first_name', 'last_name', 'age', 'season', 'season_id']

class TribeSerializer(serializers.ModelSerializer):
    season_id = serializers.IntegerField() # For POST/PUT requests

    class Meta:
        model = Tribe
        fields = ['id', 'season_id', 'name', 'color', 'is_merge_tribe']

class SurvivorTribeSerializer(serializers.ModelSerializer):
    # Add nested serializers for detailed GET responses
    survivor = SurvivorSerializer(read_only=True)
    tribe = TribeSerializer(read_only=True)

    # Add write-only fields for POST/PUT requests
    survivor_id = serializers.ImageField(write_only=True)
    tribe_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = SurvivorTribe
        fields = ['id', 'survivor', 'tribe', 'survivor_id', 'tribe_id']

class SurvivorTribes(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and managing survivor-tribe relationships
    """

    queryset = SurvivorTribe.objects.all()
    serializer_class = SurvivorTribeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Might refactor to take this out later and utilize many to many field on Models instead
        # But this might be relevant for filtering on the client side
        """
        Optionally filter survivor-tribe relationships by survivor_id,
        tribe_id, or season_id query params
        """
        queryset = SurvivorTribe.objects.all()

        survivor_id = self.request.query_params.get('survivor', None)
        tribe_id = self.request.query_params.get('tribe', None)
        season_id = self.request.query_params.get('season', None)

        if survivor_id:
            queryset = queryset.filter(survivor_id=survivor_id)
        if tribe_id:
            queryset = queryset.filter(tribe_id=tribe_id)
        if season_id:
            queryset = queryset.filter(season_id=season_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Method for admin user to create a survivor-tribe relationship"""
        try:
            survivor = Survivor.objects.get(pk=request.data["survivor_id"])
            tribe = Tribe.objects.get(pk=request.data["tribe_id"])

            if survivor.season_id != tribe.season.id:
                return Response(
                    {"reason": "Survivor and tribe must be from the same season"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            survivor_tribe = SurvivorTribe.objects.create(
                survivor=survivor,
                tribe=tribe
            )

            serializer = SurvivorTribeSerializer(survivor_tribe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response(
                {"reason": ex.args[0]}, 
                status=status.HTTP_400_BAD_REQUEST
            )