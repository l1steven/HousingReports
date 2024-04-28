import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from loginApp.models import Complaint, ComplaintFile
