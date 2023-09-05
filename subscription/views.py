from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import StripeSubscriptionForm
from django.conf import settings
import os
from datetime import datetime, timedelta
from .models import Subscription
from django.contrib.auth.forms import UserCreationForm
import stripe

from django.views.decorators.csrf import csrf_exempt
 
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.http import JsonResponse

from django.db.models.signals import post_save
from django.dispatch import receiver
# from subscription.models import User
from .models import UserProfile , Profile # import the UserProfile model
from django.contrib.auth import login

from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm
from django.contrib import messages
User = get_user_model()

# User.objects.get()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Uncommenting the line to set the Stripe API key
 
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()



 
 # Create your views here.
def homepage(request):
    return render(request, 'core/homepage.html')



def tutorials(request):
    return render(request, 'core/tutorials.html')

def contact(request):
    return render(request, 'core/contact.html')
 

from django.contrib.messages import get_messages
# Combined register_view function
def register_view(request):
    print("Register view was called.")  # Debugging line
    if request.method == 'POST':
        print("POST request received.")  # Debugging line
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("Form is valid.")  # Debugging line
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                print("Username exists, adding error message.")  # Debugging line
                messages.error(request, 'Username already exists.')
                return render(request, 'registration/register.html', {'form': form})
            else:
                print("Username does not exist, creating new user.")  # Debugging line
                # ... (rest of your code)
        else:
            print("Form is not valid.")  # Debugging line
            print(form.errors)  # Display form errors
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard_view(request):
    return render(request, 'user_dashboard.html')


from .models import UserProfile 
 
@login_required
def user_dashboard(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    stripe_customer_id = user_profile.stripe_customer_id

    # Attempt to generate a Stripe session ID for all request types (GET, POST, etc.)
    try:
        success_url = f"{settings.BASE_URL}/webhooks/stripe/payment_success/"
        cancel_url = f"{settings.BASE_URL}/webhooks/stripe/payment_cancel/"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_1NmG4RCOAyay7VTLPcRACV7i',  # Replace with your actual Stripe Price ID
                'quantity': 1,
            }],
            mode='subscription',
            customer=stripe_customer_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        stripe_session_id = checkout_session['id']
    except Exception as e:
        stripe_session_id = None
        print(f"An error occurred while creating the Stripe session: {e}")

    if request.method == "POST":
        form = StripeSubscriptionForm(request.POST)
        if form.is_valid():
            stripe_plan_id = form.cleaned_data['stripe_plan_id']

            # Handling the Free Plan
            if stripe_plan_id == 'price_1NmG4RCOAyay7VTLqfqUxOud':
                Subscription.objects.get_or_create(
                    user_profile=user_profile,
                    defaults={
                        'start_date': datetime.now(),
                        'end_date': datetime.now() + timedelta(days=30),
                        'stripe_plan_id': stripe_plan_id,
                    }
                )
                messages.success(request, 'You are now subscribed to the Free plan!')
                return redirect('dashboard')
                
            # Handling the Premium Plan
            elif stripe_plan_id == 'price_1NmG4RCOAyay7VTLPcRACV7i':
                messages.success(request, 'Please proceed to payment.')
                
    else:
        form = StripeSubscriptionForm()

    # Common context for both GET and POST
    context = {
        'form': form,
        'STRIPE_PUBLIC_KEY': os.getenv('STRIPE_PUBLIC_KEY'),
        'stripe_session_id': stripe_session_id  # Now available for all types of requests
    }

    return render(request, 'user_dashboard.html', context)



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





# Webhook handler for Stripe



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


