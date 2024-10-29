from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SeasonLog(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    season = models.ForeignKey("Season", models.CASCADE)
    status = models.CharField(max_length=50)
    created_on = models.DateTimeField(default=timezone.now)
    completed_on = models.DateTimeField(null=True, blank=True)