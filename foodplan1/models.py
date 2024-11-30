from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    AGE_CHOICES = [
        ('18-25', '18-25'),
        ('26-35', '26-35'),
        ('36-45', '36-45'),
        ('46+', '46+'),
    ]
    TRIMESTER_CHOICES = [
        ('1', 'First'),
        ('2', 'Second'),
        ('3', 'Third'),
    ]
    ALLERGY_CHOICES = [
        ('none', 'None'),
        ('nuts', 'Nuts'),
        ('dairy', 'Dairy'),
        ('gluten', 'Gluten'),
        ('shellfish', 'Shellfish'),
        ('other', 'Other'),
    ]
    GENETIC_CONDITION_CHOICES = [
        ('none', 'None'),
        ('diabetes', 'Diabetes'),
        ('hypertension', 'Hypertension'),
        ('heart-disease', 'Heart Disease'),
        ('other', 'Other'),
    ]
    FOOD_HABITS_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('non-vegetarian', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.CharField(max_length=50, choices=AGE_CHOICES)
    trimester = models.CharField(max_length=10, choices=TRIMESTER_CHOICES)
    allergy = models.CharField(max_length=100, choices=ALLERGY_CHOICES, blank=True, null=True)
    genetic_condition = models.CharField(max_length=100, choices=GENETIC_CONDITION_CHOICES, blank=True, null=True)
    food_habits = models.CharField(max_length=100, choices=FOOD_HABITS_CHOICES)

    def __str__(self):
        return f"Profile of {self.user.username}"
    
    
class Meals(models.Model):
    recipe = models.TextField(db_column='Recipe', blank=True, null=True)  # Field name made lowercase.
    mealtype = models.TextField(db_column='MealType', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'meals'


class PregnancyDietaryNeeds(models.Model):
    recipe = models.TextField(db_column='Recipe', blank=True, null=True)  # Field name made lowercase.
    cuisine = models.TextField(db_column='Cuisine', blank=True, null=True)  # Field name made lowercase.
    calories = models.IntegerField(db_column='Calories', blank=True, null=True)  # Field name made lowercase.
    protein = models.FloatField(db_column='Protein', blank=True, null=True)  # Field name made lowercase.
    vitamin_b9 = models.IntegerField(db_column='Vitamin_B9', blank=True, null=True)  # Field name made lowercase.
    vitamin_d = models.IntegerField(db_column='Vitamin_D', blank=True, null=True)  # Field name made lowercase.
    vitamin_a = models.IntegerField(db_column='Vitamin_A', blank=True, null=True)  # Field name made lowercase.
    iron = models.FloatField(db_column='Iron', blank=True, null=True)  # Field name made lowercase.
    calcium = models.IntegerField(db_column='Calcium', blank=True, null=True)  # Field name made lowercase.
    omega_3 = models.FloatField(db_column='Omega_3', blank=True, null=True)  # Field name made lowercase.
    iodine = models.IntegerField(db_column='Iodine', blank=True, null=True)  # Field name made lowercase.
    trimester = models.TextField(db_column='Trimester', blank=True, null=True)  # Field name made lowercase.
    genetic_condition = models.TextField(db_column='Genetic_Condition', blank=True, null=True)  # Field name made lowercase.
    allergy = models.TextField(db_column='Allergy', blank=True, null=True)  # Field name made lowercase.
    food_habit = models.TextField(db_column='Food_Habit', blank=True, null=True)  # Field name made lowercase.
    activity_level = models.TextField(db_column='Activity_Level', blank=True, null=True)  # Field name made lowercase.
    age = models.IntegerField(db_column='Age', blank=True, null=True)  # Field name made lowercase.
    height = models.IntegerField(db_column='Height', blank=True, null=True)  # Field name made lowercase.
    weight = models.IntegerField(db_column='Weight', blank=True, null=True)  # Field name made lowercase.
    ingredients = models.TextField(db_column='Ingredients', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pregnancy_dietary_needs'