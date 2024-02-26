from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    if request.user.groups.filter(name = 'Site Admin').exists():
        return render(request, 'loginApp/AdminDashboard.html')
    else:
        return render(request, 'loginApp/UserDashboard.html')
