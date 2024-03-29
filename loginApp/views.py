import mimetypes
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse
from .models import Complaint
from .forms import ComplaintForm
from mysite  import settings
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
                        message = f'Dear {request.user.username},\n\nYour complaint status has changed to: {complaint.get_status_display()}.\n\nComplaint details:\n- Name: {complaint.name}\n- Location: {complaint.location}\n- Description: {complaint.description}\n'
                        if status == 'reviewed':
                            message += f'Review notes: {review}\nWe appreciate your patience as we reviewed your complaint. Thank you for bringing this issue to our attention. Your input is invaluable to us in ensuring a safe and comfortable environment'
                        else:
                            message += f'Your complaint is now being actively addressed. We are committed to resolving it as swiftly as possible. You will receive further updates as we progress. Please feel free to reach out if you have any questions or need additional assistance in the meantime.'
                            
                        send_mail(
                            subject,
                            message,
                            settings.EMAIL_HOST_USER,
                            [complaint.user.email],
                            fail_silently=False,
                        )

                    return render(request, 'loginApp/complaintviews.html', {'complaints': complaint})

      return render(request, 'loginApp/complaintviews.html', {'complaints': complaint})
