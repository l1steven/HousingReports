from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from loginApp.forms import ComplaintForm


@login_required
def dashboard(request):
    if request.user.is_superuser:
        return render(request, 'loginApp/AdminDashboard.html')
    else:
        return render(request, 'loginApp/UserDashboard.html')

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

@login_required
def complaint_success(request):
    return render(request, 'loginApp/complaint_success.html')