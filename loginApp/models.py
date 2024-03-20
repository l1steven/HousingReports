from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('notreviewed', 'Not Reviewed'),
        ('in_progress', 'In Progress'),
        ('reviewed', 'Reviewed'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200) 
    description = models.TextField()
    upload = models.FileField(upload_to='uploads/%Y/%m/%d/', null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='notreviewed')
    review = models.CharField(max_length=100)


    def __str__(self):
        return f"Complaint by {'Anonymous' if self.is_anonymous else self.user.username}"
