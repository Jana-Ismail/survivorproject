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
        fields = ['is_active', 'is_juror', 'episode_voted_out', 'is']

class SurvivorLogs(viewsets.ModelViewSet):
    """
    ViewSet for viewing and updating survivor logs in an active season log
    """

    queryset = SurvivorLog.objects.get()
    serializer_class = SurvivorLogSerializer
    permission_classes = permissions.IsAuthenticated

# [
#     {
#         "model": "survivorapi.seasonlog",
#         "pk": 2,
#         "fields": {
#             "user_id": 3,
#             "season_id": 1,
#             "status": "active"
#         }
#     }
# ]