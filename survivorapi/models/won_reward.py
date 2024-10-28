from django.db import models

class WonReward(models.Model):
    episode_log = models.ForeignKey('EpisodeLog', on_delete=models.CASCADE, related_name='won_rewards')
    survivor_log = models.ForeignKey('SurvivorLog', on_delete=models.CASCADE, related_name='won_rewards')
    
    @property
    def points(self):
        """
        Points value for winning a reward
        Returns: int -- Number of points (1) for winning a reward
        """
        return 3
    
    @classmethod
    def get_stats_for_survivor(cls, survivor_log_id: int) -> dict:
        """
        Get reward stats for a specific survivor

        Args: survivor_log_id (int) -- The survivor log ID to get stats for

        Returns: dict -- Stats including count and points
        """
        count = cls.objects.filter(survivor_log_id=survivor_log_id).count()
        return {
            'count': count,
            'points': count * 1
        }

    class Meta:
        verbose_name = "found idol"
        verbose_name_plural = "found idols"
        unique_together = ['episode_log', 'survivor_log']
