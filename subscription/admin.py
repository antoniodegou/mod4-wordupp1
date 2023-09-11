# from django.contrib import admin
# from .models import CustomUser, Subscription ,ActivityLog , UserProfile # Import the necessary models

# admin.site.register( UserProfile)
# admin.site.register(CustomUser)
# admin.site.register(Subscription)

# admin.site.register(ActivityLog)


from django.contrib import admin
from .models import CustomUser, Subscription, ActivityLog, UserProfile
import logging

STRIPE_PLAN_CHOICES = [
    ('price_1NmG4RCOAyay7VTLqfqUxOud', 'Free'),
    ('price_1NmG4RCOAyay7VTLPcRACV7i', 'Premium'),
    # ('free_plan_id', 'Free'),
    # ('premium_plan_id', 'Premium')
]

logger = logging.getLogger(__name__)


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0

class ActivityLogInline(admin.TabularInline):
    model = ActivityLog
    extra = 0

def get_subscription_type(obj):
    try:
        return obj.profile.subscription.stripe_plan_id
    except:
        return "N/A"
get_subscription_type.short_description = "Subscription Type"

class CustomUserAdmin(admin.ModelAdmin):
    inlines = [UserProfileInline, ActivityLogInline]
    list_display = ['username', 'email', get_subscription_type]
    readonly_fields = ['user_subscription']

   
    def user_subscription(self, obj):
        print("user_subscription function called")

        try:
            # Try to fetch the profile
            profile = getattr(obj, 'profile', None)
            if not profile:
                return "N/A"

            # Try to fetch the subscription from the profile
            subscription = getattr(profile, 'subscription', None)
            print("AA " + str(subscription))
            print("AA", subscription)
            if not subscription:
                return "N/A"

            # Try to get the stripe_plan_id
            stripe_plan_id = getattr(subscription, 'stripe_plan_id', None)
            print("BB ", stripe_plan_id)
            if not stripe_plan_id:
                return "N/A"

            # Map the stripe_plan_id to its display name
            for plan_id, name in STRIPE_PLAN_CHOICES:
                if stripe_plan_id == plan_id:
                    return name
        except Exception as e:
            logger.error(f"Error fetching subscription for user {obj.email}: {str(e)}")
        return "N/A"

 
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ActivityLog)


# def user_subscription(self, obj):
#     print("user_subscription function called")

#     try:
#         # Try to fetch the profile
#         profile = getattr(obj, 'profile', None)
#         if not profile:
#             return "N/A"

#         # Try to fetch the subscription from the profile
#         subscription = getattr(profile, 'subscription', None)
#         print("AA "+ subscription)
#         if not subscription:
#             return "N/A"

#         # Try to get the stripe_plan_id
#         stripe_plan_id = getattr(subscription, 'stripe_plan_id', None)
#         print("BB "+ stripe_plan_id)
#         if not stripe_plan_id:
#             return "N/A"

#         # Map the stripe_plan_id to its display name
#         for plan_id, name in Subscription.STRIPE_PLAN_CHOICES:
#             if stripe_plan_id == plan_id:
#                 return name
#     except Exception as e:
#         logger.error(f"Error fetching subscription for user {obj.email}: {str(e)}")
#     return "N/A"

# def user_subscription(self, obj):
#     return "Test Subscription"

get_subscription_type.short_description = "Subscription Type"
readonly_fields = ['user_subscription']
