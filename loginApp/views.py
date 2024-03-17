import mimetypes
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Complaint
from .forms import ComplaintForm


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
            return redirect('complaint_success_anon')
    else:
        # when it is a GET request
        form = ComplaintForm(initial={'name': 'Anonymous'})
        form.fields['name'].widget.attrs['readonly'] = True
    return render(request, 'loginApp/anonymous_complaint_form.html', {'form': form})

@login_required
def complaint_success(request):
    return render(request, 'loginApp/complaint_success.html')

def complaint_success_anon(request):
    return render(request, 'loginApp/complaint_success_anon.html')
