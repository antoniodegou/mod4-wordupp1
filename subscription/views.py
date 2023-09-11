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
from .forms import CustomUserCreationForm 
from .models import Subscription, UserProfile
from django.contrib.auth.forms import PasswordChangeForm
from .models import ActivityLog
import stripe
import logging
from django.conf import settings
from .models import CustomUser as User
from django.views.decorators.http import require_POST

import traceback
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

logger = logging.getLogger(__name__)
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
            
            # Create a Stripe Customer
            customer = stripe.Customer.create(email=user.email)
            
            # # Save the Stripe Customer ID to the user's profile
            user_profile = UserProfile(user=user, stripe_customer_id=customer.id)
            user_profile.save()

            # Create or Update Stripe Customer and Assign Free Subscription
            create_or_update_stripe_customer(user)
            handle_free_plan(user_profile, 'price_1NmG4RCOAyay7VTLqfqUxOud')  # Assuming 'price_1NmG4RCOAyay7VTLqfqUxOud' is your free plan ID

            messages.success(request, 'Registration successful.')
            activity = ActivityLog(user=user, activity="User registered successfully.")
            activity.save()

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



def create_stripe_checkout_session(stripe_customer_id, price_id='price_1NmG4RCOAyay7VTLPcRACV7i'):
    """
    Create a Stripe checkout session.
    Arguments:
        - stripe_customer_id: Stripe Customer ID.
        - price_id: Stripe Price ID for the product/subscription.
    Returns:
        - Stripe session ID if successful, None otherwise.
    """
    try:
        success_url = f"{settings.BASE_URL}/subscription/webhooks/stripe/payment_success/"
        cancel_url = f"{settings.BASE_URL}/subscription/webhooks/stripe/payment_cancel/"
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            customer=stripe_customer_id,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'integration_check': 'accept_a_payment',
            }
        )
        return checkout_session['id']
    except Exception as e:
        logger.error(f"An error occurred while creating the Stripe session: {e}")
        return None




def handle_form_submission(form, user_profile,request):
    """
    Handle form submissions and validations.
    Arguments:
        - form: StripeSubscriptionForm form object.
        - user_profile: UserProfile object.
    """
    stripe_plan_id = form.cleaned_data['stripe_plan_id']
    print(f"Selected plan ID: {stripe_plan_id}")  # Debug print
    if stripe_plan_id == 'price_1NmG4RCOAyay7VTLqfqUxOud':
        handle_free_plan(user_profile, stripe_plan_id)
    elif stripe_plan_id == 'price_1NmG4RCOAyay7VTLPcRACV7i':
        handle_premium_plan(user_profile, stripe_plan_id)


def handle_free_plan(user_profile, stripe_plan_id):
    """
    Handle Free plan subscriptions.
    Arguments:
        - user_profile: UserProfile object.
        - stripe_plan_id: Stripe Plan ID for the free tier.
    """
    print(f"Handling free plan for user: {user_profile.user.username}")  # Debug print
    print("AAA")
    subscription, created = Subscription.objects.get_or_create(
        user_profile=user_profile,
        defaults={
            'start_date': datetime.now(),
            # 'end_date': datetime.now() + timedelta(days=30),
            'end_date': datetime.now()  + timedelta(minutes=3),
            'stripe_plan_id': stripe_plan_id,
            'status': 'active'  # or 'free' if you want a separate status for free plans
        }
    )

    if not created:
        # Update other fields if subscription already exists
        subscription.start_date = datetime.now()
        # subscription.end_date = datetime.now() + timedelta(days=30)
        subscription.end_date = datetime.now() + timedelta(minutes=3)
        subscription.stripe_plan_id = stripe_plan_id
        subscription.status = 'active'  # or 'free'
        subscription.save()

    print(f"Subscription details: {subscription.stripe_plan_id}, Created: {created}")  # Debug print



def handle_premium_plan(user_profile, stripe_plan_id,request):
    """
    Handle Premium plan subscriptions.
    Arguments:
        - user_profile: UserProfile object.
        - stripe_plan_id: Stripe Plan ID.
    """
    print(f"Handling premium plan for user: {request.user.username}, Stripe Plan ID: {stripe_plan_id}")
    
    subscription, created = Subscription.objects.get_or_create(
        user_profile=user_profile,
        defaults={
            'start_date': datetime.now(),
            # 'end_date': datetime.now() + timedelta(days=30),  # Adjust this based on your premium plan duration
            'end_date': datetime.now()  + timedelta(minutes=3),  # Adjust this based on your premium plan duration
            'stripe_plan_id': stripe_plan_id,
        }
    )
    if not created:
        # Update other fields if subscription already exists
        subscription.start_date = datetime.now()
        # subscription.end_date = datetime.now() + timedelta(days=30)  # Adjust this based on your premium plan duration
        subscription.end_date = datetime.now() + timedelta(minutes=3)

        subscription.stripe_plan_id = stripe_plan_id
        subscription.status = 'active'
        subscription.save()


    messages.success(request, 'You are now subscribed to the Premium plan!')

from django.views.decorators.cache import never_cache








@never_cache
@login_required
def user_dashboard(request):
    """
    Handles the user dashboard view.
    Arguments:
        - request: HTTP request object.
    """
    user_profile, _ = get_or_create_user_profile(request.user)
    
    # Check if user has a stripe_customer_id. If not, create a Stripe customer for them.
    if not user_profile.stripe_customer_id:
        customer = stripe.Customer.create(email=request.user.email)
        user_profile.stripe_customer_id = customer.id
        user_profile.save()

    stripe_session_id = create_stripe_checkout_session(user_profile.stripe_customer_id)
    
    # Fetching the Subscription
    try:
        user_subscription = Subscription.objects.get(user_profile=user_profile)
        subscription_plan = user_subscription.stripe_plan_id  # This should be either 'free' or 'premium' or your Stripe Plan ID
        renewal_date = user_subscription.end_date  # Get the renewal date

    except Subscription.DoesNotExist:
        subscription_plan = None
        renewal_date = None




    STRIPE_PLAN_NAMES = {
        # 'free_plan_id': 'Free',
        'price_1NmG4RCOAyay7VTLPcRACV7i': 'Premium',
        'price_1NmG4RCOAyay7VTLqfqUxOud': 'Free',
        # 'premium_plan_id': 'Premium'
    }
    print("DEBUG: User's subscription plan:", subscription_plan)
    subscription_plan_name = STRIPE_PLAN_NAMES.get(subscription_plan, 'Unknown Plan!')

    password_form = PasswordChangeForm(request.user)
    stripe_session_id = create_stripe_checkout_session(user_profile.stripe_customer_id)

    # Retrieve the last 10 activities for the user
    activities = ActivityLog.objects.filter(user=request.user)[:10]
    # Check the previous plan before the most recent change

    previous_subscription_plan = None
    if subscription_plan == 'price_1NmG4RCOAyay7VTLqfqUxOud' and renewal_date and renewal_date > timezone.now():
        previous_subscription_plan = 'Premium'


    context = {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'stripe_session_id': stripe_session_id,
        'subscription_plan': subscription_plan_name,  # Adding the subscription plan to the context
        'password_form': password_form,
        'previous_subscription_plan': previous_subscription_plan,
        'activities': activities,
        'renewal_date': renewal_date,
    }

    return render(request, 'user_dashboard.html', context)




 


def payment_success(request):
    # In a real-world application, you'd use the Stripe API to verify the payment
    # and potentially the session ID that Stripe passes back as a GET parameter.

    user_profile, _ = get_or_create_user_profile(request.user)

    # Update the user's subscription status in your database here.
    user_subscription = Subscription.objects.get(user_profile=user_profile)
    user_subscription.stripe_plan_id = "price_1NmG4RCOAyay7VTLPcRACV7i"  # Replace with your Stripe's premium plan ID
    user_subscription.save()

    messages.success(request, 'Your payment was successful!')
    activity = ActivityLog(user=request.user, activity=f"You are now subscribed to the Premium plan!")
    activity.save()
    return redirect('dashboard')

 
 
"""
Stripe Webhook Handlers
-----------------------
These functions are triggered by Stripe events and update the application state accordingly.
"""
 


 


"""
stripe_webhook and request
"""
@csrf_exempt
def stripe_webhook(request):
    logger.info("Received a Stripe webhook event.")
    
    try:
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        event_type = event['type']

        if event_type == 'checkout.session.completed':
            handle_checkout_session_completed(event)

        elif event_type == 'customer.subscription.deleted':
            handle_subscription_deleted(event)

        elif event_type == 'invoice.payment_succeeded':
            handle_payment_succeeded(event)

    except ValueError as e:
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status': 'failure', 'error': str(e)}, status=500)

    return JsonResponse({'status': 'success'})


"""
get_user_from_customer and customer_id
"""
def get_user_from_customer(customer_id):
    customer = stripe.Customer.retrieve(customer_id)
    try:
        return User.objects.get(email=customer.email)
    except User.DoesNotExist:
        logger.error(f"No user found for the email {customer.email}.")
        return None


"""
handle_checkout_session_completed and event
"""
def handle_checkout_session_completed(event):
    logger.info("Handling checkout.session.completed event.")
    
    session = event['data']['object']
    user = get_user_from_customer(session.get('customer'))
    
    handle_successful_payment(user, session)
    handle_subscription(user, session)


"""
handle_successful_payment and user, session
"""
def handle_successful_payment(user, session):
    payment_amount = session['amount_total'] / 100  # Convert to dollars
    if user:
        activity_message = f"Payment of ${payment_amount} was successful!"
        ActivityLog.objects.create(user=user, activity=activity_message)
    if session.get('mode') != 'subscription':
        logger.error("Received a session completed event that's not related to a subscription.")
        return JsonResponse({'status': 'failure', 'error': 'Invalid session type'}, status=400)


"""
handle_subscription and user, session
"""
def handle_subscription(user, session):
    customer_id = session.get('customer')
    if not customer_id:
        logger.info("Customer key missing in session data.")
        return JsonResponse({'status': 'failure', 'error': 'Customer key missing'}, status=400)

    subscription_id = session.get('subscription')
    if not subscription_id:
        return JsonResponse({'status': 'failure'}, status=400)

    stripe_subscription = stripe.Subscription.retrieve(subscription_id)
    stripe_plan_id = stripe_subscription['plan']['id']
    logger.info(f"Stripe Plan ID from Webhook: {stripe_plan_id}")

    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return JsonResponse({'status': 'failure'}, status=400)

    try:
        subscription = Subscription.objects.get(user_profile=user_profile)
        logger.info(f"Found existing subscription for user: {user.username}")
    except Subscription.DoesNotExist:
        logger.info(f"Creating new subscription for user: {user.username}")
        subscription = Subscription.objects.create(
            user_profile=user_profile,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(minutes=3),
            status='active',
        )

    logger.info(f"Updating subscription for user: {user.username} with Plan ID: {stripe_plan_id}")
    subscription.stripe_subscription_id = subscription_id
    subscription.stripe_plan_id = stripe_plan_id
    subscription.status = 'active'
    subscription.save()
    logger.info(f"Updated subscription for user: {user.username}")


"""
handle_subscription_deleted and event
"""
def handle_subscription_deleted(event):
    session = event['data']['object']
    customer_id = session.get('customer')

    if not customer_id:
        return JsonResponse({'status': 'failure'}, status=400)

    user = get_user_from_customer(customer_id)
    if not user:
        return JsonResponse({'status': 'failure', 'error': f'User not found for customer ID {customer_id}.'}, status=400)

    try:
        subscription = Subscription.objects.get(user=user)
    except ObjectDoesNotExist:
        return HttpResponse(status=400)

    subscription.status = 'canceled'
    subscription.save()
    logger.info(f"Subscription for user {user.username} has been canceled.")


"""
handle_payment_succeeded and event
"""
def handle_payment_succeeded(event):
    invoice = event['data']['object']
    payment_amount = invoice['amount_paid'] / 100  # Convert cents to dollars
    
    customer_email = invoice.get('customer_email')
    if not customer_email:
        customer_id = invoice.get('customer')
        user = get_user_from_customer(customer_id)
    else:
        try:
            user = User.objects.get(email=customer_email)
        except User.DoesNotExist:
            logger.error(f"No user found for the email {customer_email}.")
            return JsonResponse({'status': 'failure', 'error': f'User with email {customer_email} does not exist.'}, status=400)

    activity_message = f"Recurring payment of ${payment_amount} was successful!"
    ActivityLog.objects.create(user=user, activity=activity_message)
    logger.info(activity_message)




# This could be part of your register_view or another view
def create_or_update_stripe_customer(user):
    try:
        logger.info(f"Creating Stripe customer for email: {user.email}")
        customer = stripe.Customer.create(email=user.email)
        logger.info(f"Stripe Customer Created: {customer.id}, {customer.email}")

        # Save Stripe customer ID to UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.stripe_customer_id = customer.id
        user_profile.save()
        logger.info(f"Saved stripe_customer_id {customer.id} for user {user.email}")

        # If the UserProfile was just created, assign them the free subscription
        if created:
            handle_free_plan(user_profile, 'price_1NmG4RCOAyay7VTLqfqUxOud')

    except Exception as e:
        logger.error(f"Failed to create Stripe customer: {e}")


"""
FOR USER PROFILE DASHBOARD
"""



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


def get_recent_activities(request):
    activities = ActivityLog.objects.filter(user=request.user)[:10]  # get the last 10 activities
    return JsonResponse({'activities': [act.activity for act in activities]})


"""
FOR USER SUBSCRIPTION DASHBOARD
"""


# @login_required
# def delete_account(request):
#     """
#     Handle account and subscription deletion for the logged-in user.
#     """
#     user = request.user

#     # Cancel user's Stripe subscription if exists
#     try:
#         user_profile = UserProfile.objects.get(user=user)
#         customer_id = user_profile.stripe_customer_id
#         subscriptions = stripe.Customer.list_subscriptions(customer_id)
#         for sub in subscriptions['data']:
#             stripe.Subscription.delete(sub.id)
#     except Exception as e:
#         logger.error(f"Failed to delete Stripe subscription: {e}")

#     # Delete the user's associated data here, if any
#     # For example, you might have other models tied to the user
#     # that you'd like to delete or modify.

#     # Delete the user's account
#     user.delete()

#     # messages.success(request, "Account successfully deleted.")
#     return redirect('/')  # Or wherever you want to redirect after account deletion

@login_required
def delete_account(request):
    # Check if the request method is POST (to avoid accidental deletions)
    if request.method == 'POST':
        
        # Ensure the user is authenticated
        if request.user.is_authenticated:
            
            # Get the user object
            user_to_delete = request.user
            
            # Delete the user (this will also handle cascade deletes if set up in models)
            user_to_delete.delete()
            
            # Show a success message (optional)
            messages.success(request, 'Your account has been deleted successfully.')
            deleted_user = User.objects.filter(username=user_to_delete.username).first()
            print("Deleted user:", deleted_user)
            # Redirect to home page or any other page after successful deletion
            return redirect('/')  # Replace 'home' with the name of the desired redirect URL pattern

        else:
            messages.error(request, 'You do not have permission to delete this account.')
            return redirect('login')  # Redirect to login page

    else:
        # If not a POST request, redirect to a confirmation page or show an error
        messages.error(request, 'Invalid request.')
        return redirect('login')  # Replace 'account' with the name of the user's account page URL pattern



@login_required
@require_POST
def upgrade_subscription(request):
    """Initiate the process for upgrading a user's subscription to premium."""
    user_profile, _ = get_or_create_user_profile(request.user)
    
    # Redirect the user to Stripe for payment
    stripe_session_id = create_stripe_checkout_session(user_profile.stripe_customer_id)
    
    if not stripe_session_id:
        messages.error(request, "Failed to initiate payment with Stripe.")
        return redirect('dashboard')

    return redirect(f"https://checkout.stripe.com/pay/{stripe_session_id}")


@login_required
def downgrade_subscription(request):
    """
    Handle logic after a successful downgrade to a free subscription.
    """
    user_profile, _ = get_or_create_user_profile(request.user)
    
    # Here, you would use Stripe's API to confirm the successful downgrade
    # and update the user's subscription status in your database.

    # Assuming you've saved the user's new subscription status:
    user_subscription = Subscription.objects.get(user_profile=user_profile)
    user_subscription.stripe_plan_id = "price_1NmG4RCOAyay7VTLqfqUxOud"  # Replace with your Stripe's free plan ID
    user_subscription.save()

    messages.success(request, "Successfully downgraded to Free plan.")
    activity = ActivityLog(user=request.user, activity="Downgraded to the Free plan.")
    activity.save()
    return redirect('dashboard')


# @login_required
# @require_POST
# def upgrade_subscription(request):
#     """Handle logic for upgrading a user's subscription to premium."""
#     user_profile, _ = get_or_create_user_profile(request.user)
#     handle_premium_plan(user_profile, 'price_1NmG4RCOAyay7VTLPcRACV7i', request)  # Replace with your premium plan ID
#     activity = ActivityLog(user=request.user, activity="Upgraded to the Premium plan.")
#     activity.save()

#     messages.success(request, 'Successfully upgraded to the Premium plan!')
#     return redirect('dashboard')

# @login_required
# @require_POST
# def downgrade_subscription(request):
#     """Handle logic for downgrading a user's subscription to free."""
#     user_profile, _ = get_or_create_user_profile(request.user)
#     handle_free_plan(user_profile, 'price_1NmG4RCOAyay7VTLqfqUxOud')  # Replace with your free plan ID
#     activity = ActivityLog(user=user_profile.user, activity="Downgraded to the Free plan.")
#     activity.save()

#     messages.success(request, 'Successfully downgraded to the Free plan.')
#     return redirect('dashboard')