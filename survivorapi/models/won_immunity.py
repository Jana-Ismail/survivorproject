from django.db import models

class WonImmunity(models.Model):
    """Model for tracking immunity wins by survivors"""

    episode_log = models.ForeignKey('EpisodeLog', on_delete=models.CASCADE, related_name='won_immunities')
    survivor_log = models.ForeignKey('SurvivorLog', on_delete=models.CASCADE, related_name='won_immunities')
    is_individual = models.BooleanField(default=False)
    
    @property
    def points(self):
        """
        Points value for winning immunity
        
        Returns: int -- Number of points (3 for individual, 1 for team)
        """
        return 3 if self.is_individual else 1
    
    @classmethod
    def get_stats_for_survivor(cls, survivor_log_id: int) -> dict:
        """
        Get immunity stats for a specific survivor

        Args:
            survivor_log_id (int) -- The survivor log ID to get stats for

        Returns:
            dict -- Stats including individual and team counts and points
        """
        individual_wins = cls.objects.filter(
            survivor_log_id=survivor_log_id,
            is_individual=True
        ).count()

        team_wins = cls.objects.filter(
            survivor_log_id=survivor_log_id,
            is_individual=False
        ).count()

        return {
            'individual': {
                'count': individual_wins,
                'points': individual_wins * 3
            },
            'team': {
                'count': team_wins,
                'points': team_wins * 1
            }
        }

    class Meta:
        verbose_name = "won immunity"
        verbose_name_plural = "won immunities"
        unique_together = ['episode_log', 'survivor_log']