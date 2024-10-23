from django.db import models

class Season(models.Model):
    season_number = models.IntegerField()
    name = models.CharField(max_length=100, null=True)
    is_current = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100)