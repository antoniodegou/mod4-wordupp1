from django.shortcuts import render, redirect
from .forms import SubscriptionForm
# subscription/views.py

from django.http import HttpResponse
# Create your views here.

def create_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subscription_success')  # Redirect to a success page
    else:
        form = SubscriptionForm()
    return render(request, 'create_subscription.html', {'form': form})

def subscription_success(request):
    return render(request, 'subscription_success.html')




def subscribe(request):
    # Logic for handling a new subscription will go here
    return HttpResponse("Subscribe to Wordupp.")

def unsubscribe(request):
    # Logic for handling unsubscription will go here
    return HttpResponse("Unsubscribed from Wordupp.")

def success(request):
    # Logic for successful subscription
    return HttpResponse("Subscription successful.")

def cancel(request):
    # Logic for subscription cancellation
    return HttpResponse("Subscription cancelled.")
