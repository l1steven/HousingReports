import mimetypes
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Complaint
from .forms import ComplaintForm
from mysite import settings
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import Thread, Post
import boto3

@login_required
def dashboard(request):
    complaints = Complaint.objects.filter(user=request.user) if not request.user.is_superuser else Complaint.objects.all()

    for complaint in complaints:
        if complaint.upload:
            mime_type, _ = mimetypes.guess_type(complaint.upload.url)
            complaint.is_image = mime_type.startswith('image/') if mime_type else False
            complaint.is_pdf = 'application/pdf' == mime_type if mime_type else False
            complaint.is_text = 'text/plain' == mime_type if mime_type else False

    userType = 'loginApp/AdminDashboard.html' if request.user.is_superuser else 'loginApp/UserDashboard.html'
    return render(request, userType, {'complaints': complaints})


def dashboardanon(request):
    complaints = Complaint.objects.all()

    for complaint in complaints:
        if complaint.upload:
            mime_type, _ = mimetypes.guess_type(complaint.upload.url)
            complaint.is_image = mime_type.startswith('image/') if mime_type else False
            complaint.is_pdf = 'application/pdf' == mime_type if mime_type else False
            complaint.is_text = 'text/plain' == mime_type if mime_type else False

    userType = 'loginApp/AnonDashboard.html'
    return render(request, userType, {'complaints': complaints})

@login_required
def complaint_form(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            return redirect('complaint_success')
    else:
        form = ComplaintForm()
    return render(request, 'loginApp/complaint_form.html', {'form': form})

def anonymous_complaint_view(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.name = 'Anonymous'
            complaint.user = None
            complaint.is_anonymous = True
            complaint.save()
            return render(request, 'loginApp/complaint_success_anon.html')
    else:
        # when it is a GET request
        form = ComplaintForm(initial={'name': 'Anonymous'})
        form.fields['name'].widget.attrs['readonly'] = True
    return render(request, 'loginApp/anonymous_complaint_form.html', {'form': form})

@login_required
def complaint_success(request):
    return render(request, 'loginApp/complaint_success.html')


def deletecomplaintcommon(request, complaint_id): 
    complaint = Complaint.objects.filter(id=complaint_id).first()
    s3_key = complaint.upload.name
    if complaint is not None:
        complaint.delete()
        s3 = boto3.client('s3')
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_key)
    complaints = Complaint.objects.filter(user=request.user)
    return render(request, 'loginApp/UserDashboard.html', {'complaints': complaints})
    

@login_required
def editcomplaintcommon(request, complaint): 
    complaint1 = Complaint.objects.filter(id=complaint).first()
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES, instance=complaint1)
        if form.is_valid():
            form.save()
            return redirect('complaint_success')
    else: 
        form = ComplaintForm(instance=complaint1)

    return render(request, 'loginApp/edit_form.html', {'form': form})
class ThreadListView(ListView):
    template_name="thread_list.html"
    context_object_name="list"
    def get_queryset(self):
        return Thread.objects.order_by("-created_at")

class ThreadDetailView(DetailView):
    model = Thread

class CreateThreadView(CreateView):
    model = Thread
    fields = ['title']
    success_url = reverse_lazy('thread_list')

class CreatePostView(CreateView):
    model = Post
    fields = ['content']
    
    def form_valid(self, form):
        form.instance.thread_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('thread_detail', kwargs={'pk': self.kwargs['pk']})