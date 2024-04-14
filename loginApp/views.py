import mimetypes
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse
from .models import Complaint
from .forms import ComplaintForm
from mysite import settings
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import Thread, Post
import boto3
from urllib.parse import urlparse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
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

            if request.user.email:
                subject = "Complaint Submission Confirmed"
                message = f"Dear {request.user.username}, \n\nYour complaint has been successfully submitted and is now under review. \n\nComplaint details:\n- Name: {complaint.name}\n- Location: {complaint.location}\n- Description: {complaint.description}\n\nWe will notify you of any updates regarding your complaint status.\n\nThank you for bringing this to our attention."

            send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [request.user.email],
                    fail_silently=False,
                )

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


from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404

@login_required
def deletecomplaintcommon(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.user != complaint.user and not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete this complaint.")
        return HttpResponseRedirect(reverse('dashboard'))

    if request.method == 'POST':
        s3 = boto3.client('s3')
        s3_url = complaint.upload.url
        parsed_url = urlparse(s3_url)
        s3_key = parsed_url.path[1:] 
        try:
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_key)
        except Exception as e:
            messages.error(request, "Error deleting file from storage.")
            return HttpResponseRedirect(reverse('dashboard'))
        complaint.delete()
        messages.success(request, "Complaint deleted successfully.")
        return HttpResponseRedirect(reverse('dashboard'))
    return render(request, 'loginApp/delete_confirmation.html', {'complaint': complaint})

    

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


def handle_complaint_click(request, complaint_id): 
      complaint = Complaint.objects.filter(id=complaint_id).first()
    
      if request.method == 'POST':
            if complaint:
                status = request.POST.get('status')
                review = request.POST.get('review')
                if status in dict(Complaint.STATUS_CHOICES):
                    previous_status = complaint.status

                    complaint.status = status
                    if status == 'reviewed':
                        complaint.review = review
                    complaint.save()

                    if previous_status != status and complaint.user and complaint.user.email:
                        subject = "Complaint Update"
                        message = f'Dear {request.user.username},\n\nYour complaint status has changed to: {complaint.get_status_display()}.\n\nComplaint details:\n- Name: {complaint.name}\n- Location: {complaint.location}\n- Description: {complaint.description}\n\n'
                        if status == 'reviewed':
                            message += f'Review notes:\n{review}\n\nWe appreciate your patience as we reviewed your complaint. Thank you for bringing this issue to our attention. Your input is invaluable to us in ensuring a safe and comfortable environment'
                        else:
                            message += f'Your complaint is now being actively addressed.\n\nWe are committed to resolving it as swiftly as possible. You will receive further updates as we progress. Please feel free to reach out if you have any questions or need additional assistance in the meantime.'
                            
                        send_mail(
                            subject,
                            message,
                            settings.EMAIL_HOST_USER,
                            [complaint.user.email],
                            fail_silently=False,
                        )

                    return render(request, 'loginApp/complaintviews.html', {'complaints': complaint})

      return render(request, 'loginApp/complaintviews.html', {'complaints': complaint})

