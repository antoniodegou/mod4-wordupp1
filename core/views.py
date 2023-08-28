from django.shortcuts import render

# Create your views here.

def homepage(request):
    return render(request, 'core/homepage.html')

def pricing(request):
    return render(request, 'core/pricing.html')

def tutorials(request):
    return render(request, 'core/tutorials.html')

def contact(request):
    return render(request, 'core/contact.html')