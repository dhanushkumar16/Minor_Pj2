from django.db import models

class ScrapedData(models.Model):
    date = models.DateField()
    value = models.FloatField()

    def __str__(self):
        return f"{self.date}: {self.value}"
