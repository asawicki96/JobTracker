from django.db import models
from tracker.models import Tracker
from .fields import OrderField
# Create your models here.


class Offer(models.Model):
    foreign_identity = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    snippet = models.TextField(null=True, blank=True)
    salary = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    job_type = models.CharField(max_length=150, blank=True, null=True)
    link = models.URLField(max_length=350)
    company = models.CharField(max_length=150, null=True, blank=True)
    updated = models.DateTimeField()
    order = OrderField(blank=True, for_fields=['owner'])
    owner = models.ForeignKey(Tracker,
                       related_name='offers', 
                       on_delete=models.CASCADE, 
                       null=True, blank=True)

    class Meta:
        ordering = ['-order']

    def __str__(self):
        return self.title
