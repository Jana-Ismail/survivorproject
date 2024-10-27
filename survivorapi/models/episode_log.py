from django.db import models
from django.contrib.auth.models import User

class EpisodeLog(models.Model):
    episode = models.ForeignKey("Episode", on_delete=models.CASCADE)
    season_log = models.ForeignKey("SeasonLog", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["episode__episode_number"]
        unique_together = ['user', 'episode']  # Prevent duplicate logs for same episode
