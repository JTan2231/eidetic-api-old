from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request, username=None):
    if username is None:
        return render(request, 'pages/clusters.html')
    else:
        return render(request, 'pages/profile.html')
