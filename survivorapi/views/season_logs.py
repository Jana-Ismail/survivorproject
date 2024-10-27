"""View module for handling requests about Season Logs"""
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework import status
from django.db import transaction
from survivorapi.models import SeasonLog, Season, Survivor, SurvivorLog, FavoriteSurvivor

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

class SurvivorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Survivor
        fields = ['id', 'first_name', 'last_name', 'age', 'img_url']

class SurvivorLogSerializer(serializers.ModelSerializer):
    survivor = SurvivorSerializer(many=False)

    class Meta:
        model = SurvivorLog
        fields = ['id', 'survivor', 'is_active', 'is_juror', 'episode_voted_out', 'is_user_winner_pick', 'is_season_winner']

class FavoriteSurvivorSerializer(serializers.ModelSerializer):
    survivor_log = SurvivorLogSerializer(many=False)
    
    class Meta:
        model = FavoriteSurvivor
        fields = ['id', 'survivor_log']

class SeasonLogs(viewsets.ModelViewSet):
    """
    ViewSet for handling season-related operations for users
    """

    serializer_class = SeasonLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This method is used by retrieve, update, and destroy actions
        """
        return SeasonLog.objects.filter(user=self.request.auth.user)
    
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

            # Use transaction to ensure all-or-nothing creation of logs
            with transaction.atomic():
                # Create season log
                season_log = SeasonLog.objects.create(
                    user=user,
                    season=season,
                    status="active"
                )

                # Get all survivors for this season
                season_survivors = Survivor.objects.filter(season=season)

                # Create survivor logs for each survivor
                survivor_logs = [
                    SurvivorLog(
                        survivor=survivor,
                        user=user,
                        season_log = season_log,
                        is_active=True,
                        is_juror=False,
                        is_user_winner_pick=False,
                        episode_voted_out=None,
                        is_season_winner=False
                    ) for survivor in season_survivors
                ]

                # Bulk create all survivor logs
                SurvivorLog.objects.bulk_create(survivor_logs)
                
            serializer = SeasonLogSerializer(season_log)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
         
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Handle DELETE operations for removing a season log"""
        
        try:
            with transaction.atomic():
                season_log = Season.objects.get(pk=pk)

                # Delete related survivor logs first
                SurvivorLog.objects.filter(
                    user=request.auth.user,
                    survivor__season=season_log.season
                ).delete()

                # Then delete the season log
                season_log.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except SeasonLog.DoesNotExist:
            return Response({"message": "Season log not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get', 'put'], url_path="survivors")
    def survivor_logs(self, request, pk=None):
        season_log = self.get_object()
        if request.method == 'GET':
            survivor_logs = SurvivorLog.objects.filter(season_log=season_log)
            serializer = SurvivorLogSerializer(survivor_logs, many=True)
            return Response(serializer.data)
        
        # Need to add logic for updating survivor-logs
        # But also this logic might exist in other methods, like the episode_log method
        elif request.method == 'PUT':
            pass

    @action(detail=True, methods=['get', 'post'], url_path='survivors/favorites')
    def favorite_survivors(self, request, pk=None, favorite_pk=None):
        """
        Handle favorite survivors for a season log
        """
        season_log = self.get_object()

        if request.method == 'GET':
            favorites = FavoriteSurvivor.objects.filter(
                survivor_log__season_log=season_log,
                survivor_log__user=request.auth.user
            )
            serializer = FavoriteSurvivorSerializer(favorites, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            survivor_log_id = request.data.get("survivor_log_id")

            if not survivor_log_id:
                return Response(
                    {"message": "survivor_log_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Verify the survivor_log exists and belongs to this season_log
                survivor_log = SurvivorLog.objects.get(
                    pk=survivor_log_id,
                    season_log=season_log,
                    user=request.auth.user
                )

                # Check if already a favorite
                existing_favorite = FavoriteSurvivor.objects.filter(
                    survivor_log=survivor_log
                ).first()

                if existing_favorite:
                    return Response(
                        {"message": "This survivor is already a favorite"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                favorite = FavoriteSurvivor.objects.create(
                    survivor_log=survivor_log
                )

                serializer = FavoriteSurvivorSerializer(favorite)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            except SurvivorLog.DoesNotExist:
                return Response(
                    {"message": "Invalid survivor_log_id"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            except Exception as ex:
                return Response(
                    {"reason": ex.args[0]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
    @action(detail=True, methods=['delete'], url_path='survivors/favorites/(?P<favorite_pk>[^/.]+)?')
    def delete_favorites(self, request, pk=None, favorite_pk=None):
        """Handle DELETE for a specific favorite"""

        season_log = self.get_object()
        try:
            favorite = FavoriteSurvivor.objects.get(
                pk=favorite_pk,
                survivor_log__season_log=season_log,
                survivor_log__user=request.auth.user
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FavoriteSurvivor.DoesNotExist:
            return Response(
                {"message": "Favorite not found"},
                status=status.HTTP_404_NOT_FOUND
            )