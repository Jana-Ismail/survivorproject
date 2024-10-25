from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from survivorapi.models import SurvivorLog, Survivor

class SurvivorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survivor
        fields = ['id', 'first_name', 'last_name', 'age']

class SurvivorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurvivorLog
        fields = ['id', 'is_active', 'is_juror', 'episode_voted_out', 'season_log_id', 'is_user_winner_pick', 'is_season_winner']

class SurvivorLogs(viewsets.ModelViewSet):
    """
    ViewSet for viewing and updating survivor logs in an active season log
    """

    # queryset = SurvivorLog.objects.all()
    serializer_class = SurvivorLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filters survivor logs based on user permissions"""
        user = self.request.auth.user
        if user.is_staff:
            return SurvivorLog.objects.all()

        return SurvivorLog.objects.filter(
            user=user
        )