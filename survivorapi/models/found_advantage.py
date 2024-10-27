from django.db import models

class FoundAdvantage(models.Model):
    """Model for tracking advantages found by survivors"""
    episode_log = models.ForeignKey("EpisodeLog", on_delete=models.CASCADE, related_name="found_advantages")
    survivor_log = models.ForeignKey("SurvivorLog", on_delete=models.CASCADE, related_name="found_advantages")

    @property
    def points(self):
        """
        Points value for finding an advantage

        Returns: int -- Number of points (2) for finding an advantage
        """
        return 2
    
    @classmethod
    def get_stats_for_survivor(cls, survivor_log_id: int) -> dict:
        """Get advantage stats for a specific survivor
        
        Args: survivor_log_id (int): The survivor log ID to get stats for
        
        Returns: dict -- status including count and points
        """
        count = cls.objects.filter(survivor_log_id=survivor_log_id).count()
        
        return {
            'count': count,
            'points': count * 2
        }
    
    class Meta:
        verbose_name = "found advantage"
        verbose_name_plural = "found advantages"
