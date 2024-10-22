from django.db import models
from django.contrib.auth.models import User

class SeasonLog(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    season = models.ForeignKey("Season", models.CASCADE)
    status = models.CharField(max_length=50)