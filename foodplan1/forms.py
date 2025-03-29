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

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match!")
        
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with this email already exists!")
        return username

from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    TRIMESTER_CHOICES = [
        ('First', 'First Trimester (Weeks 1-12)'),
        ('Second', 'Second Trimester (Weeks 13-26)'),
        ('Third', 'Third Trimester (Weeks 27-40)'),
        ('Preconception', 'Preconception Planning')
    ]

    ALLERGY_CHOICES = [
        ('No Allergy', 'No Allergy'),
        ('Dairy', 'Dairy'),
        ('Gluten', 'Gluten'),
        ('Peanuts', 'Peanuts'),
        ('Seafood', 'Seafood'),
        ('Soy', 'Soy'),
    ]

    GENETIC_CONDITION_CHOICES = [
        ('No Condition', 'No Condition'),
        ('Anemia', 'Anemia'),
        ('Blood Pressure', 'Blood Pressure'),
        ('Diabetes', 'Diabetes'),
        ('High Cholesterol', 'High Cholesterol'),
    ]

    FOOD_HABITS_CHOICES = [
        ('Vegetarian', 'Vegetarian'),
        ('Vegan', 'Vegan'),
        ('Non-vegetarian', 'Non-vegetarian'),
    ]


    trimester = forms.ChoiceField(
        choices=TRIMESTER_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    allergy = forms.MultipleChoiceField(
        choices=ALLERGY_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control multi-select'}),
        required=False
    )

    genetic_condition = forms.MultipleChoiceField(
        choices=GENETIC_CONDITION_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control multi-select'}),
        required=False
    )

    food_habits = forms.ChoiceField(
        choices=FOOD_HABITS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ['age', 'trimester', 'allergy', 'genetic_condition', 'food_habits']