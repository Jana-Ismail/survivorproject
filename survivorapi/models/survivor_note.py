from django.db import models

class SurvivorNote(models.Model):
    survivor_log = models.ForeignKey("SurvivorLog", on_delete=models.CASCADE)
    text = models.TextField()