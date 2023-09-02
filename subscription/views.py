from django.shortcuts import render, redirect
 
from django.contrib.auth.decorators import login_required
import stripe
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Subscription 
from datetime import datetime, timedelta
from django.contrib import messages
from dotenv import load_dotenv
from .forms import StripeSubscriptionForm
from django.conf import settings
from django.conf import settings
import stripe
import os

# Uncommenting the line to set the Stripe API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


# stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
print("lAAAAA",stripe.api_key)
print("lBBBBB",stripe.api_key)
 # Create your views here.
def homepage(request):
    return render(request, 'core/homepage.html')



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



# @login_required
# def user_dashboard(request):
#     if request.method == "POST":
#         form = SubscriptionForm(request.POST)
#         if form.is_valid():
#             subscription, created = Subscription.objects.get_or_create(
#                 user=request.user,
#                 defaults={
#                     'start_date': datetime.now(),
#                     'end_date': datetime.now() + timedelta(days=30),
#                     'is_premium': form.cleaned_data['is_premium'],
#                 }
#             )
#             if not created:
#                 subscription.is_premium = form.cleaned_data['is_premium']
#                 subscription.start_date = datetime.now()
#                 subscription.end_date = datetime.now() + timedelta(days=30)
#                 subscription.save()

#             messages.success(request, 'Subscription updated successfully!')
#             return redirect('dashboard')
#     else:
#         form = SubscriptionForm()
    
#     return render(request, 'user_dashboard.html', {'form': form})
print("AAAAA  AAAA AAAA   AAAA")
print("Stripe Secret Key:", settings.STRIPE_SECRET_KEY)
@login_required
def user_dashboard(request):
    if request.method == "POST":
        form = StripeSubscriptionForm(request.POST)
        if form.is_valid():
            stripe_plan_id = form.cleaned_data['stripe_plan_id']
            
            # Process Stripe payment if premium plan is selected
            if stripe_plan_id == 'premium':
                # Here, you'd normally use Stripe's API to handle the payment
                pass
            
            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'start_date': datetime.now(),
                    'end_date': datetime.now() + timedelta(days=30),
                    'stripe_plan_id': stripe_plan_id,
                }
            )
            if not created:
                subscription.stripe_plan_id = stripe_plan_id
                subscription.save()

            messages.success(request, 'Subscription updated successfully!')
            return redirect('dashboard')
    else:
        form = StripeSubscriptionForm()
    
    success_url = f"{settings.BASE_URL}/payment_success/"
    cancel_url = f"{settings.BASE_URL}/payment_cancel/"

    # Create a Stripe Checkout Session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'premium',  # Replace with your actual Stripe Price ID
            'quantity': 1,
        }],
        mode='subscription',
        success_url=success_url,
        cancel_url=cancel_url,
    )

    context = {
        'form': form,
        'STRIPE_PUBLIC_KEY': stripe.api_key,
        'stripe_session_id': checkout_session['id']
    }

    return render(request, 'user_dashboard.html', context)
