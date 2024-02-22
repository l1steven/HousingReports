from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    if request.user.is_superuser:
        return render(request, 'AdminDashboard.html')
    else:
        return render(request, 'user_dashboard.html')
