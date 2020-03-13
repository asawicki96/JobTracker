from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Tracker(models.Model):
    owner = models.ForeignKey(User, related_name='trackers', on_delete=models.CASCADE)
    keywords = models.CharField(max_length=350)
    location = models.CharField(max_length=100, blank=True, null=True)
    radius = models.IntegerField(null=True, blank=True)
    salary = models.IntegerField(null=True, blank=True)
    page = models.IntegerField(null=True, blank=True)
    time = models.TimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return 'Tracker: {}'.format(self.keywords)
