from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def bootstrap_server(request):
    return render(request, 'bootstrap/server.html')