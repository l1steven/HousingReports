from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    description = models.TextField()
    upload = models.FileField(upload_to='uploads/%Y/%m/%d/', null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint by {'Anonymous' if self.is_anonymous else self.user.username}"
    
class Thread(models.Model):
    title=models.CharField(max_length=200)
    created_at=models.DateTimeField(auto_now_add=True)
class Post(models.Model):
    thread=models.ForeignKey(Thread,on_delete=models.CASCADE)
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)