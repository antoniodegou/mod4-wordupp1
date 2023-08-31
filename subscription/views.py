from django.shortcuts import render, redirect
from .forms import SubscriptionForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import stripe
from django.contrib.auth.forms import UserCreationForm
# from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from .forms import SubscriptionForm  # Importing SubscriptionForm from forms.py
from .models import Subscription 
 
from datetime import datetime, timedelta
from django.contrib import messages
from .forms import SubscriptionForm
 

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

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard_view(request):
    return render(request, 'user_dashboard.html')

@login_required
def profile_view(request):
    return render(request, 'profile.html')


@login_required
def user_dashboard(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'start_date': datetime.now(),
                    'end_date': datetime.now() + timedelta(days=30),
                    'is_premium': form.cleaned_data['is_premium'],
                }
            )
            if not created:
                subscription.is_premium = form.cleaned_data['is_premium']
                subscription.start_date = datetime.now()
                subscription.end_date = datetime.now() + timedelta(days=30)
                subscription.save()

            messages.success(request, 'Subscription updated successfully!')
            return redirect('user_dashboard')
    else:
        form = SubscriptionForm()
    
    return render(request, 'user_dashboard.html', {'form': form})

