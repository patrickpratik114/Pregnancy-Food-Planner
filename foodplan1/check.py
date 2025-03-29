from django.db import models
from django.contrib.auth.models import User

# Profile model with choices for age, trimester, allergy, genetic condition, and food habits.
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


# Meals model represents a simple meal table. Here we use managed = False if you don't want Django to handle migrations.
class Meals(models.Model):
    id = models.AutoField(primary_key=True)
    recipe = models.TextField(db_column='Recipe', blank=True, null=True)
    mealtype = models.TextField(db_column='MealType', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'meals'

    def __str__(self):
        return f"Meal {self.id}"


# PregnancyDietaryNeeds model updated to include a cuisine field and adjusted field names.
class PregnancyDietaryNeeds(models.Model):
    recipe = models.TextField(db_column='Recipe', blank=True, null=True)
    cuisine = models.TextField(db_column='Cuisine', blank=True, null=True)
    calories = models.IntegerField(db_column='Calories', blank=True, null=True)
    protein = models.FloatField(db_column='Protein', blank=True, null=True)
    vitamin_b9 = models.IntegerField(db_column='Vitamin_B9', blank=True, null=True)
    vitamin_d = models.IntegerField(db_column='Vitamin_D', blank=True, null=True)
    vitamin_a = models.IntegerField(db_column='Vitamin_A', blank=True, null=True)
    iron = models.FloatField(db_column='Iron', blank=True, null=True)
    calcium = models.IntegerField(db_column='Calcium', blank=True, null=True)
    omega_3 = models.FloatField(db_column='Omega_3', blank=True, null=True)
    iodine = models.IntegerField(db_column='Iodine', blank=True, null=True)
    trimester = models.TextField(db_column='Trimester', blank=True, null=True)
    genetic_condition = models.TextField(db_column='Genetic_Condition', blank=True, null=True)
    allergy = models.TextField(db_column='Allergy', blank=True, null=True)
    food_habit = models.TextField(db_column='Food_Habit', blank=True, null=True)
    activity_level = models.TextField(db_column='Activity_Level', blank=True, null=True)
    age = models.IntegerField(db_column='Age', blank=True, null=True)
    height = models.IntegerField(db_column='Height', blank=True, null=True)
    weight = models.IntegerField(db_column='Weight', blank=True, null=True)
    ingredients = models.TextField(db_column='Ingredients', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pregnancy_dietary_needs'

    def __str__(self):
        return f"Pregnancy Dietary Needs: {self.recipe}"


# MealPlan model uses a JSONField to store a meal plan, along with a helper method to clear a specific day.
class MealPlan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.JSONField(default=dict)

    def clear_day(self, day):
        """Remove a specific day's meals from the plan."""
        if day in self.plan:
            del self.plan[day]
            self.save()

    def __str__(self):
        return f"MealPlan for {self.user.username}"
