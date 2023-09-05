from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_exempt
import stripe
import os
from datetime import datetime, timedelta
import traceback
from .forms import CustomUserCreationForm, StripeSubscriptionForm
from .models import UserProfile, Subscription
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
# Set Stripe API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

User = get_user_model()

def homepage(request):
    return render(request, 'core/homepage.html')


def tutorials(request):
    return render(request, 'core/tutorials.html')

def contact(request):
    return render(request, 'core/contact.html')

@login_required
def dashboard_view(request):
    return render(request, 'user_dashboard.html')

def payment_success(request):
    # In a real-world application, you'd use the Stripe API to verify the payment
    # and potentially the session ID that Stripe passes back as a GET parameter.

    # Update the user's subscription status in your database here.
    # For example, change their 'role' from 'free' to 'premium', or extend their subscription date.

    messages.success(request, 'Your payment was successful!')
    return redirect('dashboard')


# Dummy function to handle the checkout session. Replace this with your actual logic.
def handle_checkout_session(session):
    print("Checkout session completed:", session)
    # Here, you could look up the user associated with this session and mark them as having paid,
    # enroll them in a course, or whatever else your application needs to do.




@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create or update a user profile when a user is created or updated.
    Arguments:
        - sender: The model class sending the signal.
        - instance: The instance of the model.
        - created: A boolean indicating whether the instance was just created.
    """
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()



def register_view(request):
    """
    Handles user registration with custom form.
    Arguments:
        - request: HTTP request object.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'registration/register.html', {'form': form})
            else:
                form.save()
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})



@login_required
def user_dashboard(request):
    """
    Displays the user dashboard and handles Stripe subscriptions.
    Arguments:
        - request: HTTP request object.
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    stripe_customer_id = user_profile.stripe_customer_id

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1NmG4RCOAyay7VTLPcRACV7i',
                'quantity': 1,
            }],
            mode='subscription',
            customer=stripe_customer_id,
            success_url=f"{settings.BASE_URL}/webhooks/stripe/payment_success/",
            cancel_url=f"{settings.BASE_URL}/webhooks/stripe/payment_cancel/",
        )
        stripe_session_id = checkout_session['id']
    except Exception as e:
        stripe_session_id = None

    if request.method == "POST":
        form = StripeSubscriptionForm(request.POST)
        if form.is_valid():
            stripe_plan_id = form.cleaned_data['stripe_plan_id']
            # Add your logic to handle Free and Premium plans here
    else:
        form = StripeSubscriptionForm()

    context = {
        'form': form,
        'STRIPE_PUBLIC_KEY': os.getenv('STRIPE_PUBLIC_KEY'),
        'stripe_session_id': stripe_session_id
    }

    return render(request, 'user_dashboard.html', context)

@csrf_exempt
def stripe_webhook(request):
    """
    Handles Stripe webhook events for subscription management.
    Arguments:
        - request: HTTP request object containing webhook data from Stripe.
    """
    try:
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            handle_checkout_session(session)
        elif event['type'] == 'customer.subscription.deleted':
            session = event['data']['object']
            handle_subscription_deleted(session)
        else:
            print(f"Unhandled event type {event['type']}")

    except ValueError as e:
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=500)

    return JsonResponse({'status': 'success'})



def handle_checkout_session(session):
    """
    Handles a completed Stripe checkout session.
    Arguments:
        - session: A Stripe Session object containing the details of a completed checkout session.
    """
    try:
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')

        if not customer_id or not subscription_id:
            return JsonResponse({'status': 'failure'}, status=400)

        stripe_subscription = stripe.Subscription.retrieve(subscription_id)
        stripe_plan_id = stripe_subscription['plan']['id']

        customer = stripe.Customer.retrieve(customer_id)
        user = User.objects.get(email=customer.email)
        user_profile = UserProfile.objects.get(user=user)

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
        
    except Exception as e:
        print(f"An error occurred while handling the checkout session: {e}")
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=400)


def handle_subscription_deleted(session):
    """
    Handles a deleted Stripe customer subscription.
    Arguments:
        - session: A Stripe Session object containing the details of a deleted subscription.
    """
    try:
        customer_id = session.get('customer')
        if not customer_id:
            return JsonResponse({'status': 'failure'}, status=400)

        customer = stripe.Customer.retrieve(customer_id)
        user = User.objects.get(email=customer.email)

        try:
            subscription = Subscription.objects.get(user=user)
        except ObjectDoesNotExist:
            return HttpResponse(status=400)

        subscription.status = 'canceled'
        subscription.save()
        
    except Exception as e:
        print(f"An error occurred while handling the subscription deletion: {e}")
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=400)


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


