from django import forms
from .models import Subscription  # Import your model here

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['stripe_plan_id']