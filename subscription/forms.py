from django import forms
from .models import Subscription  # Import your model here

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['is_premium']  # Include is_premium here