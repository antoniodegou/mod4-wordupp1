from django import forms
from .models import Subscription  # Import your model here
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
 
class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['stripe_plan_id']



class StripeSubscriptionForm(forms.Form):
    STRIPE_PLAN_CHOICES = [
        ('price_1NmG4RCOAyay7VTLqfqUxOud', 'Free'),
        ('price_1NmG4RCOAyay7VTLPcRACV7i', 'Premium ($1.99/month)'),
    ]
    
    stripe_plan_id = forms.ChoiceField(choices=STRIPE_PLAN_CHOICES, widget=forms.RadioSelect)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")