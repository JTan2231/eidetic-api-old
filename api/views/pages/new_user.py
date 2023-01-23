from django.shortcuts import render

def index(request):
    return render(request, 'pages/new_user.html')
