from django.db import models

class FavoriteSurvivor(models.Model):
    survivor_log = models.ForeignKey("SurvivorLog", on_delete=models.CASCADE)
    season = models.ForeignKey('Season', on_delete=models.CASCADE)
