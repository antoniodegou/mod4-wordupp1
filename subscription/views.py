from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import StripeSubscriptionForm
import stripe
from django.conf import settings
import os
from datetime import datetime, timedelta
from .models import Subscription
from django.contrib.auth.forms import UserCreationForm
import stripe
import os

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
# Uncommenting the line to set the Stripe API key
 
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
# print("Stripe Public Key: ", os.getenv('STRIPE_PUBLIC_KEY'))

 
@login_required
def user_dashboard(request):
    if request.method == "POST":
        form = StripeSubscriptionForm(request.POST)
        if form.is_valid():
            stripe_plan_id = form.cleaned_data['stripe_plan_id']

            # Handling the Free Plan
            if stripe_plan_id == 'free':
                Subscription.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'start_date': datetime.now(),
                        'end_date': datetime.now() + timedelta(days=30),
                        'stripe_plan_id': stripe_plan_id,
                    }
                )
                messages.success(request, 'You are now subscribed to the Free plan!')
                return redirect('dashboard')

            # Handling the Premium Plan
            elif stripe_plan_id == 'premium':
                try:
                    success_url = f"{settings.BASE_URL}/payment_success/"
                    cancel_url = f"{settings.BASE_URL}/payment_cancel/"

                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price': 'premium',  # Your actual Stripe Price ID here
                            'quantity': 1,
                        }],
                        mode='subscription',
                        success_url=success_url,
                        cancel_url=cancel_url,
                    )

                    context = {
                        'form': form,
                        'STRIPE_PUBLIC_KEY': os.getenv('STRIPE_PUBLIC_KEY'),
                        'stripe_session_id': checkout_session['id']
                    }

                    messages.success(request, 'Please proceed to payment.')
                    return render(request, 'user_dashboard.html', context)

                except Exception as e:
                    messages.error(request, f"An error occurred: {e}")
    else:
        form = StripeSubscriptionForm()

    context = {
        'form': form,
        'STRIPE_PUBLIC_KEY': os.getenv('STRIPE_PUBLIC_KEY'),
    }

    return render(request, 'user_dashboard.html', context)


def payment_success(request):
    # In a real-world application, you'd use the Stripe API to verify the payment
    # and potentially the session ID that Stripe passes back as a GET parameter.

    # Update the user's subscription status in your database here.
    # For example, change their 'role' from 'free' to 'premium', or extend their subscription date.

    messages.success(request, 'Your payment was successful!')
    return redirect('dashboard')