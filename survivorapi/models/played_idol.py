from django.db import models

class PlayedIdol(models.Model):
    episode_log = models.ForeignKey('EpisodeLog', on_delete=models.CASCADE, related_name='played_idols')
    survivor_log = models.ForeignKey('SurvivorLog', on_delete=models.CASCADE, related_name='played_idols')
    
    @property
    def points(self):
        """
        Points value for playing an idol
        
        Returns: int -- Number of points (2) for playing an idol
        """
        return 2
    
    @classmethod
    def get_stats_for_survivor(cls, survivor_log_id: int) -> dict:
        """
        Get played idol stats for a specific survivor
        
        Args: survivor_log_id (int): The survivor log ID to get stats for
        
        Returns: dict -- Stats including count and points
        """
        count = cls.objects.filter(survivor_log_id=survivor_log_id).count()
        return {
            'count': count,
            'points': count * 3
        }
