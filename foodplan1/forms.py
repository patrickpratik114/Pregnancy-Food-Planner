from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile

class UserSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'password']
        labels = {'username': 'Email'}

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Check if passwords match
        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match!")
        
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Ensure the email (username) is unique
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with this email already exists!")
        return username


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['age', 'trimester', 'allergy', 'genetic_condition', 'food_habits']
        widgets = {
            'age': forms.Select(),
            'trimester': forms.Select(),
            'allergy': forms.Select(choices=Profile.ALLERGY_CHOICES),
            'genetic_condition': forms.Select(choices=Profile.GENETIC_CONDITION_CHOICES),
            'food_habits': forms.Select(choices=Profile.FOOD_HABITS_CHOICES),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Add any profile-specific validation here if necessary
        return cleaned_data
