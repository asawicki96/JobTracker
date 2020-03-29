from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Tracker(models.Model):

    RADIUS_CHOICES = [
        (0, 0),
        (8, 8),
        (16, 16),
        (24, 24),
        (40, 40),
    ]


    owner = models.ForeignKey(User, related_name='trackers', on_delete=models.CASCADE)
    keywords = models.CharField(max_length=350)
    location = models.CharField(max_length=100, blank=True, null=True)
    radius = models.IntegerField(default=None, choices=RADIUS_CHOICES, null=True, blank=True)
    salary = models.IntegerField(null=True, blank=True)
    page = models.IntegerField(null=True, blank=True)
    time = models.TimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    size = models.IntegerField(default=50, blank=True)
    
    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return 'Tracker: {}'.format(self.keywords)
 
    