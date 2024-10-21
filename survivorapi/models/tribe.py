from django.db import models

class Tribe(models.Model):
    season = models.ForeignKey('Season', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    is_merge_tribe = models.BooleanField(default=False)