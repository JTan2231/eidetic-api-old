from django.shortcuts import render

def index(request, entry_id=None):
    return render(request, 'pages/entry_viewer.html')
