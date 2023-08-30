from django.shortcuts import render, redirect
from .forms import SubscriptionForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import stripe
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

stripe.api_key = 'pk_test_51NkmkJCOAyay7VTL9sF0N6bNUBccALv9Qn0Do0RYuOn4UHJaaDhBsSxYW45cf2gRxSLonu7kh4rLFW84kL7OfZQ1002UaUb385'

 
@login_required  # Ensures that only logged-in users can access this view
def create_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            # Populate the user field with the current user
            subscription = form.save(commit=False)
            subscription.user = request.user  # Set the user field
            subscription.save()  # Now save the form

            # Stripe subscription logic could go here

            return redirect('subscription_success')  # Redirect to a success page
        else:
            print("Form is not valid")
            print(form.errors)
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

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# Create your views here.
def homepage(request):
    return render(request, 'core/homepage.html')

def pricing(request):
    return render(request, 'core/pricing.html')

def tutorials(request):
    return render(request, 'core/tutorials.html')

def contact(request):
    return render(request, 'core/contact.html')

