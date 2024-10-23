"""View module for handling requests about Season Logs"""

from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from survivorapi.models import SeasonLog, Season

class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [
            'id', 'season_number', 'name', 'location',
            'start_date', 'end_date', 'is_current'
        ]

class SeasonLogSerializer(serializers.ModelSerializer):
    season = SeasonSerializer(many=False)
    
    class Meta:
        model = SeasonLog
        fields = ['id', 'status', 'season']

class SeasonLogs(viewsets.ModelViewSet):
    """
    ViewSet for handling season-related operations for users
    """

    def list(self, request):
        user = request.auth.user

        # Filter season logs by status directly from the database
        active_seasons = SeasonLog.objects.filter(user=user, status="active")
        completed_seasons = SeasonLog.objects.filter(user=user, status="complete")
        
        # Get all seasons and exclude the ones that already have a season log for the user
        logged_seasons = SeasonLog.objects.filter(user=user).values_list('season_id', flat=True)
        inactive_seasons = Season.objects.exclude(id__in=logged_seasons)

        serialized_active_seasons = SeasonLogSerializer(active_seasons, many=True).data
        serialized_completed_seasons = SeasonLogSerializer(completed_seasons, many=True).data
        serialized_inactive_seasons = SeasonSerializer(inactive_seasons, many=True).data

        response_data = {
            "active": serialized_active_seasons,
            "complete": serialized_completed_seasons,
            "inactive": serialized_inactive_seasons
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def create(self, request):
        """Handle POST operations for creating a new season log"""
        user = request.auth.user
        season_id = request.data.get("season_id")
        
        try:
            season = Season.objects.get(pk=season_id)

            # Check to see if season log already exists in the database for user
            existing_log = SeasonLog.objects.filter(user=user, season=season).first()
            if existing_log:
                return Response(
                    {"message": "A season log for this season already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            season_log = SeasonLog()
            season_log.user = request.auth.user
            season_log.season = season
            season_log.status = "active"
            season_log.save()
                
            serializer = SeasonLogSerializer(season_log)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
         
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Handle DELETE operations for removing a season log"""
        
        try:
            season_log = SeasonLog.objects.get(pk=pk)
            season_log.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except SeasonLog.DoesNotExist:
            return Response({"message": "Season log not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
