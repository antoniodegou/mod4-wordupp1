from django import forms
from .models import Subscription  # Import your model here
from django.contrib.auth.forms import UserCreationForm
from subscription.models import CustomUser
 
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
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user