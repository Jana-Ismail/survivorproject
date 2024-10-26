from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from survivorapi.models import SurvivorLog, FavoriteSurvivor, Survivor

class SurvivorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survivor
        fields = ['id', 'first_name', 'last_name', 'age']

class SurvivorLogSerializer(serializers.ModelSerializer):
    survivor = SurvivorSerializer(many=False)

    class Meta:
        model = SurvivorLog
        fields = ['id', 'survivor', 'is_active', 'is_juror',
                  'episode_voted_out', 'is_user_winner_pick',
                  'is_season_winner']

class FavoriteSurvivorSerializer(serializers.ModelSerializer):
    survivor_log = SurvivorLogSerializer(many=False)

    class Meta:
        model = FavoriteSurvivor
        fields = ['id', 'survivor_log']

class FavoriteSurvivors(viewsets.ModelViewSet):
    """
    ViewSet to manage a user's favorite survivors in a season log
    """
    queryset = FavoriteSurvivor.objects.all()
    serializer_class = FavoriteSurvivorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        A method to enable a user to create a favorite survivor
        for their current season log
        """
        survivor_log_id = request.data["survivor_log_id"]
        survivor_log = SurvivorLog.objects.get(pk=survivor_log_id)
        try:
            favorite_survivor = FavoriteSurvivor.objects.create(
                survivor_log = survivor_log
            )

            serializer = FavoriteSurvivorSerializer(favorite_survivor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
