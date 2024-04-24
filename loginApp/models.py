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
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='notreviewed')
    review = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Complaint by {'Anonymous' if self.is_anonymous else self.user.username}"

class ComplaintFile(models.Model):
    complaint = models.ForeignKey(Complaint, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='complaint_files/%Y/%m/%d/')

class Thread(models.Model):
    title=models.CharField(max_length=200)
    created_at=models.DateTimeField(auto_now_add=True)
class Post(models.Model):
    thread=models.ForeignKey(Thread,on_delete=models.CASCADE)
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
