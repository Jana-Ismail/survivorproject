from django.db import models

class Episode(models.Model):
    season = models.ForeignKey("Season", on_delete=models.CASCADE, related_name="episodes")
    episode_number = models.IntegerField()
    air_date_time = models.DateTimeField()
    title = models.CharField(max_length=255)
    
    class Meta:
        ordering = ["episode_number"]
        unique_together = ['season', 'episode_number']  # Prevent duplicate episode numbers in a season

