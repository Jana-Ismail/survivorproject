"""View module for handling requests about Season Logs"""
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework import status
from django.db import transaction
from survivorapi.models import (
    SeasonLog, 
    Season, 
    Survivor, 
    SurvivorLog, 
    FavoriteSurvivor, 
    SurvivorNote, 
    EpisodeLog, 
    Episode,
    FoundAdvantage,
    FoundIdol,
    WonImmunity,
    WonReward,
    PlayedIdol
)

class SeasonSerializer(serializers.ModelSerializer):
    total_episodes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Season
        fields = [
            'id', 'season_number', 'name', 'location',
            'start_date', 'end_date', 'is_current',
            'total_episodes'
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
        fields = [
            'id', 'survivor', 'is_active', 
            'is_juror', 'episode_voted_out', 
            'is_user_winner_pick', 'is_season_winner'
        ]

class FavoriteSurvivorSerializer(serializers.ModelSerializer):
    survivor_log = SurvivorLogSerializer(many=False)
    
    class Meta:
        model = FavoriteSurvivor
        fields = ['id', 'survivor_log']

class SurvivorNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurvivorNote
        fields = ['id', 'text']

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ['id', 'episode_number', 'air_date_time', 'title']

class FoundIdolSerializer(serializers.ModelSerializer):
    survivor_log = SurvivorLogSerializer(many=False)
    
    class Meta:
        model = FoundIdol
        fields = ['id', 'survivor_log']

class FoundAdvantageSerializer(serializers.ModelSerializer):
    survivor_log = SurvivorLogSerializer(many=False)
    
    class Meta:
        model = FoundAdvantage
        fields = ['id', 'survivor_log']

class PlayedIdolSerializer(serializers.ModelSerializer):
    survivor_log = SurvivorLogSerializer(many=False)
    
    class Meta:
        model = PlayedIdol
        fields = ['id', 'survivor_log']

class WonImmunitySerializer(serializers.ModelSerializer):
    survivor_log = SurvivorLogSerializer(many=False)
    
    class Meta:
        model = WonImmunity
        fields = ['id', 'survivor_log', 'is_individual']

class WonRewardSerializer(serializers.ModelSerializer):
    survivor_log = SurvivorLogSerializer(many=False)
    
    class Meta:
        model = WonReward
        fields = ['id', 'survivor_log']

class EpisodeLogSerializer(serializers.ModelSerializer):
    episode = EpisodeSerializer(many=False)
    found_idols = FoundIdolSerializer(many=True, read_only=True)
    found_advantages = FoundAdvantageSerializer(many=True, read_only=True)
    played_idols = PlayedIdolSerializer(many=True, read_only=True)
    won_immunities = WonImmunitySerializer(many=True, read_only=True)
    won_rewards = WonRewardSerializer(many=True, read_only=True)
    next_episode = serializers.SerializerMethodField()
    
    class Meta:
        model = EpisodeLog
        fields = ['id', 'episode', 'created_at', 'found_idols', 
                 'found_advantages', 'played_idols', 'won_immunities', 
                 'won_rewards', 'next_episode']
    
    def get_next_episode(self, obj):
        """Calculate the next episode number, considering season total"""
        current_episode = obj.episode.episode_number
        total_episodes = obj.episode.season.total_episodes

        if current_episode < total_episodes:
            return current_episode + 1
        return None

class EpisodeActionsSerializer(serializers.Serializer):
    """Serializer for actions taken by a survivor in an episode"""
    found_idol = serializers.BooleanField(required=False, default=False)
    found_advantage = serializers.BooleanField(required=False, default=False)
    played_idol = serializers.BooleanField(required=False, default=False)
    won_immunity = serializers.BooleanField(required=False, default=False)
    is_individual_immunity = serializers.BooleanField(required=False, default=False)
    won_reward = serializers.BooleanField(required=False, default=False)
    is_individual_reward = serializers.BooleanField(required=False, default=False)
    voted_out = serializers.BooleanField(required=False, default=False)

class SurvivorLogActionsSerializer(serializers.Serializer):
    """Serializer for a survivor log and its actions"""
    id = serializers.IntegerField()
    episode_actions = EpisodeActionsSerializer()

class EpisodeLogCreateSerializer(serializers.Serializer):
    """Main serializer for creating an episode log"""
    episode_number = serializers.IntegerField()
    survivor_logs = serializers.ListField(
        child=SurvivorLogActionsSerializer(),
        allow_empty=True
    )

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
        active_seasons = SeasonLog.objects.filter(
            user=user, status="active"
        ).order_by('created_on')

        completed_seasons = SeasonLog.objects.filter(
            user=user, status="complete"
        ).order_by('completed_on')
        
        # Get all seasons and exclude the ones that already have a season log for the user
        logged_seasons = SeasonLog.objects.filter(user=user).values_list('season_id', flat=True)
        inactive_seasons = Season.objects.exclude(
            id__in=logged_seasons
        ).order_by('season_number')

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
                season_log = self.get_object()

                # Delete related survivor logs first
                SurvivorLog.objects.filter(season_log=season_log).delete()

                # Then delete the season log
                season_log.delete()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except SeasonLog.DoesNotExist:
            return Response({"message": "Season log not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get', 'put'], url_path="survivors/(?P<survivor_log_pk>[^/.]+)?")
    def survivor_logs(self, request, pk=None, survivor_log_pk=None):
        season_log = self.get_object()

        if request.method == 'GET':
            if survivor_log_pk:
                try:
                    survivor_log = SurvivorLog.objects.get(
                        pk=survivor_log_pk,
                        season_log=season_log
                    )
                    serializer = SurvivorLogSerializer(survivor_log)
                    return Response(serializer.data)
                except SurvivorLog.DoesNotExist:
                    return Response(
                        {"message": "Survivor log not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                survivor_logs = SurvivorLog.objects.filter(season_log=season_log)
                serializer = SurvivorLogSerializer(survivor_logs, many=True)
                return Response(serializer.data)
        
        # Need to add logic for updating survivor-logs
        # But also this logic might exist in other methods, like the episode_log method
        elif request.method == 'PUT':
            pass

    @action(detail=True, methods=['get', 'put'], url_path='survivors/winner-pick')
    def favorite_to_win(self, request, pk=None):
        """Handle winner selection for a season log"""
        season_log = self.get_object()

        if request.method == 'GET':
            try:
                winner_pick = SurvivorLog.objects.get(
                    season_log=season_log,
                    user=request.auth.user,
                    is_user_winner_pick=True
                )
                serializer = SurvivorLogSerializer(winner_pick, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except SurvivorLog.DoesNotExist:
                # Return null when no winner is picked yet
                return Response("", status=status.HTTP_200_OK)
        if request.method == 'PUT':
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

                # Check to see if there is already a winner pick for the season log
                existing_winner_pick = SurvivorLog.objects.filter(
                    season_log=season_log,
                    is_user_winner_pick=True
                ).first()

                if existing_winner_pick:
                    existing_winner_pick.is_user_winner_pick = False
                    existing_winner_pick.save()
                
                survivor_log.is_user_winner_pick = True
                survivor_log.save()

                serializer = SurvivorLogSerializer(survivor_log, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)   
                       
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
        
    @action(detail=True, methods=['get', 'post'], url_path="survivors/(?P<survivor_log_pk>[^/.]+)/notes")
    def view_or_create_note(self, request, pk=None, survivor_log_pk=None):
        season_log = self.get_object()
        
        if request.method == 'GET':
            try:
                survivor_log = SurvivorLog.objects.get(
                    pk=survivor_log_pk,
                    season_log=season_log,
                    user=request.auth.user
                )
                notes = SurvivorNote.objects.filter(survivor_log=survivor_log)
                serializer = SurvivorNoteSerializer(notes, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except SurvivorLog.DoesNotExist:
                return Response(
                    {"message": "Survivor log not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        elif request.method == 'POST':
            try:
                # Verify the survivor_log exists and belongs to this season_log
                survivor_log = SurvivorLog.objects.get(
                    pk=survivor_log_pk,
                    season_log=season_log,
                    user=request.auth.user
                )
                # Check if text is provided so no resource is created without text data
                text = request.data.get("text")
                if not text:
                    return Response(
                        {"message": "Text is required for the note"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                note = SurvivorNote.objects.create(
                    survivor_log=survivor_log,
                    text=text
                )
                serializer = SurvivorNoteSerializer(note)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as ex:
                return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put', 'delete'], url_path="survivors/(?P<survivor_log_pk>[^/.]+)/notes/(?P<note_pk>[^/.]+)")
    def update_or_delete_note(self, request, pk=None, survivor_log_pk=None, note_pk=None):
        season_log = self.get_object()
        if request.method == 'PUT':
            try:
                survivor_log = SurvivorLog.objects.get(
                    pk=survivor_log_pk,
                    season_log=season_log,
                    user=request.auth.user
                )
                note = SurvivorNote.objects.get(
                    pk=note_pk,
                    survivor_log=survivor_log
                )
                text = request.data["text"]
                if not text:
                    return Response(
                        {"message": "Text is required for the note."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                note.text = text
                note.save()
                serializer = SurvivorNoteSerializer(note)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except SurvivorNote.DoesNotExist:
                return Response(
                    {"message": "Note not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            except Exception as ex:
                return Response({"reason": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            try:
                survivor_log = SurvivorLog.objects.get(
                    pk=survivor_log_pk,
                    season_log=season_log,
                    user=request.auth.user
                )
                note = SurvivorNote.objects.get(
                    pk=note_pk,
                    survivor_log=survivor_log
                )
                note.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            except SurvivorNote.DoesNotExist:
                return Response(
                    {"message": "Note not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            except Exception as ex:
                return Response({"reason": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get', 'post'], url_path="episodes")
    def episode_logs(self, request, pk=None):
        season_log = self.get_object()

        if request.method == 'GET':
            # Get all episode logs for the season
            episode_logs = EpisodeLog.objects.filter(
                season_log=season_log,
                user=request.auth.user
            ).order_by('episode__episode_number')

            # Get active survivors for the season
            active_survivors = SurvivorLog.objects.filter(
                season_log=season_log,
                is_active=True,
                episode_voted_out__isnull=True
            )

            # Calculate next episode number
            total_episodes = season_log.season.total_episodes
            current_episode_count = episode_logs.count()
            next_episode = None if current_episode_count >= total_episodes else current_episode_count + 1

            # Serialize the data
            serialized_episode_logs = EpisodeLogSerializer(episode_logs, many=True).data
            serialized_active_survivors = SurvivorLogSerializer(active_survivors, many=True).data

            response_data = {
                'episode_logs': serialized_episode_logs,
                'active_survivors': serialized_active_survivors,
                'next_episode': next_episode,
                'total_episodes': total_episodes
            }

            return Response(response_data, status=status.HTTP_200_OK)
        
        if request.method == 'POST':
            # Validate the request data
            serializer = EpisodeLogCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            try:
                # Get the episode instance
                episode_number = validated_data['episode_number']

                # Add validation for episode number
                if episode_number > season_log.season.total_episodes:
                    return Response(
                        {"message": f"Episode number cannot exceed season total of {season_log.season.total_episodes}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                episode = Episode.objects.get(
                    season=season_log.season,
                    episode_number=episode_number
                )
                
                # Check if episode log already exists
                existing_log = EpisodeLog.objects.filter(
                    user=request.auth.user,
                    episode=episode,
                    season_log=season_log
                ).first()

                if existing_log:
                    return Response(
                        {"message": "Episode log already exists for this episode"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Validate survivor_log ids and collect them
                survivor_logs = validated_data['survivor_logs']
                survivor_log_ids = [sl['id'] for sl in survivor_logs]
                
                valid_survivor_logs = SurvivorLog.objects.filter(
                    id__in=survivor_log_ids,
                    season_log=season_log,
                    is_active=True
                )

                if len(valid_survivor_logs) != len(survivor_log_ids):
                    return Response(
                        {"message": "One or more invalid or inactive survivor log IDs"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                with transaction.atomic():
                    # Create episode log
                    episode_log = EpisodeLog.objects.create(
                        user=request.auth.user,
                        episode=episode,
                        season_log=season_log
                    )

                    # Create lists for bulk operations
                    found_idols = []
                    found_advantages = []
                    played_idols = []
                    won_immunities = []
                    won_rewards = []
                    voted_out_logs = []

                    for survivor_data in survivor_logs:
                        survivor_log = next(
                            sl for sl in valid_survivor_logs if sl.id == survivor_data['id']
                        )
                        actions = survivor_data['episode_actions']

                        if actions.get("found_idol"):
                            found_idols.append(
                                FoundIdol(
                                    episode_log=episode_log,
                                    survivor_log=survivor_log
                                )
                            )
                        
                        if actions.get("found_advantage"):
                            found_advantages.append(
                                FoundAdvantage(
                                    episode_log=episode_log,
                                    survivor_log=survivor_log
                                )
                            )
                        
                        if actions.get("played_idol"):
                            played_idols.append(
                                PlayedIdol(
                                    episode_log=episode_log,
                                    survivor_log=survivor_log
                                )
                            )
                        
                        if actions.get("won_immunity"):
                            won_immunities.append(
                                WonImmunity(
                                    episode_log=episode_log,
                                    survivor_log=survivor_log,
                                    is_individual=actions.get("is_individual_immunity", False)
                                )
                            )
                        
                        if actions.get("won_reward"):
                            won_rewards.append(
                                WonReward(
                                    episode_log=episode_log,
                                    survivor_log=survivor_log,
                                )
                            )
                        
                        if actions.get("voted_out"):
                            survivor_log.is_active = False
                            survivor_log.episode_voted_out = episode.episode_number
                            voted_out_logs.append(survivor_log)

                    # Bulk create all action records
                    if found_idols:
                        FoundIdol.objects.bulk_create(found_idols)
                    if found_advantages:
                        FoundAdvantage.objects.bulk_create(found_advantages)
                    if played_idols:
                        PlayedIdol.objects.bulk_create(played_idols)
                    if won_immunities:
                        WonImmunity.objects.bulk_create(won_immunities)
                    if won_rewards:
                        WonReward.objects.bulk_create(won_rewards)

                    # Bulk update voted out survivors
                    if voted_out_logs:
                        SurvivorLog.objects.bulk_update(
                            voted_out_logs,
                            ['is_active', 'episode_voted_out']
                        )

                    # Refresh episode log and get updated data
                    episode_log.refresh_from_db()
                    active_survivors = SurvivorLog.objects.filter(
                        season_log=season_log,
                        is_active=True
                    )

                    response_data = {
                        'episode_log': EpisodeLogSerializer(episode_log).data,
                        'active_survivors': SurvivorLogSerializer(active_survivors, many=True).data
                    }

                    return Response(response_data, status=status.HTTP_201_CREATED)

            except Episode.DoesNotExist:
                return Response(
                    {"message": "Episode not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as ex:
                return Response(
                    {"message": str(ex)},
                    status=status.HTTP_400_BAD_REQUEST
                )