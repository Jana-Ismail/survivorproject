from django.db import models

class SurvivorTribe(models.Model):
    tribe = models.ForeignKey("Tribe", on_delete=models.CASCADE)
    survivor = models.ForeignKey("Survivor", on_delete=models.CASCADE)