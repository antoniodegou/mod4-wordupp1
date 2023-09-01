from django import forms
from .models import Subscription  # Import your model here

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['stripe_plan_id']



class StripeSubscriptionForm(forms.Form):
    STRIPE_PLAN_CHOICES = [
        ('stripe_free_plan_id_here', 'Free'),
        ('stripe_premium_plan_id_here', 'Premium ($1.99/month)'),
    ]
    
    stripe_plan_id = forms.ChoiceField(choices=STRIPE_PLAN_CHOICES, widget=forms.RadioSelect)
