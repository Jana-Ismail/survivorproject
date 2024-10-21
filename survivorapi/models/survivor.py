from django.db import models

class Survivor(models.Model):
    season = models.ForeignKey('Season', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    img_url = models.URLField()
