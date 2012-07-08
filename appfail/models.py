from django.db import models

class OccurrenceCache(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    failure_json = models.TextField()
    reported = models.BooleanField(default=False)