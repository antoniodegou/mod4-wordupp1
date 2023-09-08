from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
import os
from datetime import datetime, timedelta
from .forms import CustomUserCreationForm, StripeSubscriptionForm
from .models import Subscription, UserProfile, Profile
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

"""
My Static Pages CORE:
"""

def homepage(request):
    return render(request, 'core/homepage.html')


def tutorials(request):
    return render(request, 'core/tutorials.html')

def contact(request):
    return render(request, 'core/contact.html')


"""
My SUBSCRIPTION VIEWS: REGISTRATION
"""

def register_view(request):
    """
    Handles user registration with custom form.
    Arguments:
        - request: HTTP request object.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user and get a user object
            login(request, user)  # Log the user in

            # Create or Update Stripe Customer and Assign Free Subscription
            create_or_update_stripe_customer(user)

            messages.success(request, 'Registration successful.')
            return redirect('dashboard')  # Redirect to a new page
        else:
            messages.error(request, 'Unsuccessful registration. Invalid information.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

"""
Stripe Subscription Helpers
---------------------------
These functions assist in managing Stripe subscriptions and user profiles.
"""

def get_or_create_user_profile(user):
    """
    Initialize or retrieve the user profile.
    Arguments:
        - user: The User object.
    Returns:
        - UserProfile object.
    """
    return UserProfile.objects.get_or_create(user=user)



def create_stripe_checkout_session(stripe_customer_id):
    """
    Create a Stripe checkout session.
    Arguments:
        - stripe_customer_id: Stripe Customer ID.
    Returns:
        - Stripe session ID if successful, None otherwise.
    """
    try:
        success_url = f"{settings.BASE_URL}/webhooks/stripe/payment_success/"
        cancel_url = f"{settings.BASE_URL}/webhooks/stripe/payment_cancel/"
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1NmG4RCOAyay7VTLPcRACV7i',
                'quantity': 1,
            }],
            mode='subscription',
            customer=stripe_customer_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return checkout_session['id']
    except Exception as e:
        print(f"An error occurred while creating the Stripe session: {e}")
        return None

def handle_form_submission(form, user_profile,request):
    """
    Handle form submissions and validations.
    Arguments:
        - form: StripeSubscriptionForm form object.
        - user_profile: UserProfile object.
    """
    stripe_plan_id = form.cleaned_data['stripe_plan_id']
    if stripe_plan_id == 'price_1NmG4RCOAyay7VTLqfqUxOud':
        handle_free_plan(user_profile, stripe_plan_id, request)
    elif stripe_plan_id == 'price_1NmG4RCOAyay7VTLPcRACV7i':
        handle_premium_plan(user_profile, stripe_plan_id, request)

def handle_free_plan(user_profile, stripe_plan_id,request):
    """
    Handle Free plan subscriptions.
    Arguments:
        - user_profile: UserProfile object.
        - stripe_plan_id: Stripe Plan ID.
    """
    Subscription.objects.get_or_create(
        user_profile=user_profile,
        defaults={
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=30),
            'stripe_plan_id': stripe_plan_id,
        }
    )
    messages.success(request, 'You are now subscribed to the Free plan!')

def handle_premium_plan(user_profile, stripe_plan_id,request):
    """
    Handle Premium plan subscriptions.
    Arguments:
        - user_profile: UserProfile object.
        - stripe_plan_id: Stripe Plan ID.
    """
    messages.success(request, 'Please proceed to payment.')

@login_required
def user_dashboard(request):
    """
    Handles the user dashboard view.
    Arguments:
        - request: HTTP request object.
    """
    user_profile, _ = get_or_create_user_profile(request.user)
    stripe_session_id = create_stripe_checkout_session(user_profile.stripe_customer_id)
    # Fetching the Subscription
    try:
        user_subscription = Subscription.objects.get(user_profile=user_profile)
        subscription_plan = user_subscription.stripe_plan_id  # This should be either 'free' or 'premium' or your Stripe Plan ID
    except Subscription.DoesNotExist:
        subscription_plan = None

    STRIPE_PLAN_NAMES = {
        'price_1NmG4RCOAyay7VTLqfqUxOud': 'Free',
        'price_1NmG4RCOAyay7VTLPcRACV7i': 'Premium'
    }

    subscription_plan_name = STRIPE_PLAN_NAMES.get(subscription_plan, 'Unknown Plan!')
    
    if request.method == "POST":
        form = StripeSubscriptionForm(request.POST)
        if form.is_valid():
            handle_form_submission(form, user_profile, request)
    else:
        form = StripeSubscriptionForm()
    # Mapping Stripe Plan IDs to human-readable names
    
    password_form = PasswordChangeForm(request.user)

    context = {
        'form': form,
        'STRIPE_PUBLIC_KEY': os.getenv('STRIPE_PUBLIC_KEY'),
        'stripe_session_id': stripe_session_id,
        'subscription_plan': subscription_plan_name,  # Adding the subscription plan to the context
        'password_form': password_form
    }

    return render(request, 'user_dashboard.html', context)


def payment_success(request):
    # In a real-world application, you'd use the Stripe API to verify the payment
    # and potentially the session ID that Stripe passes back as a GET parameter.

    # Update the user's subscription status in your database here.
    # For example, change their 'role' from 'free' to 'premium', or extend their subscription date.

    messages.success(request, 'Your payment was successful!')
    return redirect('dashboard')
 
 
"""
Stripe Webhook Handlers
-----------------------
These functions are triggered by Stripe events and update the application state accordingly.
"""
 


 


import traceback
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

@csrf_exempt
def stripe_webhook(request):
    try:
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return JsonResponse({'status': 'failure', 'error': str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({'status': 'failure', 'error': str(e)}, status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            customer_id = session.get('customer')
            subscription_id = session.get('subscription')

            if not customer_id or not subscription_id:
                return JsonResponse({'status': 'failure'}, status=400)

            stripe_subscription = stripe.Subscription.retrieve(subscription_id)
            stripe_plan_id = stripe_subscription['plan']['id']

            customer = stripe.Customer.retrieve(customer_id)
            try:
                user = User.objects.get(email=customer.email)
                user_profile = UserProfile.objects.get(user=user)
            except (User.DoesNotExist, UserProfile.DoesNotExist):
                return JsonResponse({'status': 'failure'}, status=400)

            try:
                subscription = Subscription.objects.get(user_profile=user_profile)
            except Subscription.DoesNotExist:
                subscription = Subscription.objects.create(
                    user_profile=user_profile,
                    start_date=timezone.now(),
                    end_date=timezone.now() + timedelta(days=30),
                    status='active',
                )

            subscription.stripe_subscription_id = subscription_id
            subscription.stripe_plan_id = stripe_plan_id
            subscription.status = 'active'
            subscription.save()

        elif event['type'] == 'customer.subscription.deleted':
            session = event['data']['object']
            customer_id = session.get('customer')

            if not customer_id:
                return JsonResponse({'status': 'failure'}, status=400)

            customer = stripe.Customer.retrieve(customer_id)

            try:
                user = User.objects.get(email=customer.email)
            except User.DoesNotExist:
                return JsonResponse({'status': 'failure', 'error': f'User with email {customer.email} does not exist.'}, status=400)

            try:
                subscription = Subscription.objects.get(user=user)
            except ObjectDoesNotExist:
                return HttpResponse(status=400)

            subscription.status = 'canceled'
            subscription.save()

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=500)

    return JsonResponse({'status': 'success'})


# This could be part of your register_view or another view
def create_or_update_stripe_customer(user):
    try:
        print(f"Creating Stripe customer for email: {user.email}")
        customer = stripe.Customer.create(email=user.email)
        print(f"Stripe Customer Created: {customer.id}, {customer.email}")

        # Save Stripe customer ID to UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.stripe_customer_id = customer.id
        user_profile.save()
        print(f"Saved stripe_customer_id {customer.id} for user {user.email}")

        # Create or update Subscription
        subscription, created = Subscription.objects.get_or_create(
            user_profile=user_profile,
            defaults={
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=30),
                'stripe_plan_id': 'price_1NmG4RCOAyay7VTLqfqUxOud',  # Your Stripe Free Plan ID
                'status': 'active'
            }
        )
        if not created:
            # Update other fields if subscription already exists
            subscription.start_date = datetime.now()
            subscription.end_date = datetime.now() + timedelta(days=30)
            subscription.stripe_plan_id = 'price_1NmG4RCOAyay7VTLqfqUxOud'
            subscription.status = 'active'
            subscription.save()
    except Exception as e:
        print(f"Failed to create Stripe customer: {e}")


"""
FOR USER DASHBOARD
"""

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update the session hash to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})