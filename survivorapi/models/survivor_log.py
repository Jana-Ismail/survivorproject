from django.db import models
from django.contrib.auth.models import User

class SurvivorLog(models.Model):
    survivor = models.ForeignKey("Survivor", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    season_log = models.ForeignKey("SeasonLog", on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    is_juror = models.BooleanField(default=False)
    episode_voted_out = models.IntegerField(null=True, blank=True)
    is_user_winner_pick = models.BooleanField(default=False)
    is_season_winner = models.BooleanField(default=False)